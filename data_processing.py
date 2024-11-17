import pandas as pd
import re
import numpy as np
from datetime import datetime

# Define constellation mappings
CONSTELLATION_MAP = {
    1: 'GPS',
    3: 'GLONASS',
    5: 'QZSS',
    6: 'Galileo',
    7: 'BeiDou'
}

# NMEA to AGC constellation type mapping
NMEA_TO_AGC_TYPE = {
    'GP': 1,  # GPS
    'GL': 3,  # GLONASS
    'QZ': 5,  # QZSS
    'GA': 6,  # Galileo
    'BD': 7,  # BeiDou
    'GB': 7   # Alternative BeiDou prefix
}

def is_valid_snr(snr):
    """Validate SNR value"""
    try:
        snr_val = float(snr)
        return 0 <= snr_val <= 99
    except (ValueError, TypeError):
        return False

def parse_agc_file(agc_file_path):
    """Parse AGC data from the CSV file."""
    agc_data = []
    
    with open(agc_file_path, 'r') as file:
        for line in file:
            if line.startswith('Agc,'):
                parts = line.strip().split(',')
                try:
                    timestamp = int(parts[1])  # utcTimeMillis
                    agc_db = float(parts[11])  # AgcDb
                    constellation_type = int(parts[13])  # ConstellationType
                    
                    if constellation_type in CONSTELLATION_MAP:
                        agc_data.append({
                            'timestamp': timestamp,
                            'agc': agc_db,
                            'constellation_type': constellation_type
                        })
                except (IndexError, ValueError) as e:
                    continue
    
    df = pd.DataFrame(agc_data)
    if not df.empty:
        print("\nAGC Timestamps:")
        print(df['timestamp'].unique())
    return df

def parse_nmea_file(nmea_file_path):
    """Parse NMEA data focusing on GSV sentences for SNR."""
    nmea_data = []
    invalid_snr_count = 0
    
    with open(nmea_file_path, 'r') as file:
        for line in file:
            if not line.startswith('NMEA,$'):
                continue
            
            # Extract timestamp from the end of the line
            timestamp_match = re.search(r',(\d+)$', line)
            if not timestamp_match:
                continue
                
            current_timestamp = int(timestamp_match.group(1))
            parts = line.strip().split(',')
            
            if len(parts) < 2:
                continue
                
            sentence = parts[1]
            
            # Handle GSV sentences for SNR data
            if 'GSV' in sentence:
                constellation_prefix = sentence[1:3]  # Skip the $ and take next two chars
                if constellation_prefix not in NMEA_TO_AGC_TYPE:
                    continue
                    
                constellation_type = NMEA_TO_AGC_TYPE[constellation_prefix]
                
                # Process satellite information (4 satellites per sentence)
                # Format: $--GSV,total_msgs,msg_num,total_sats,sat_info(4 sets of: PRN,elevation,azimuth,SNR)
                for i in range(4, len(parts)-4, 4):
                    try:
                        if i+3 < len(parts):
                            snr_str = parts[i+3].split('*')[0]  # Remove checksum if present
                            if snr_str and snr_str != '':
                                try:
                                    snr = int(snr_str)
                                    if is_valid_snr(snr):
                                        nmea_data.append({
                                            'timestamp': current_timestamp,
                                            'snr': snr,
                                            'constellation_type': constellation_type
                                        })
                                    else:
                                        invalid_snr_count += 1
                                except ValueError:
                                    invalid_snr_count += 1
                    except (ValueError, IndexError):
                        continue
    
    if invalid_snr_count > 0:
        print(f"Warning: Filtered out {invalid_snr_count} invalid SNR values")
    
    df = pd.DataFrame(nmea_data)
    if not df.empty:
        print("\nNMEA Timestamps:")
        print(df['timestamp'].unique())
        print("\nSNR value statistics:")
        print(df['snr'].describe())
    return df if not df.empty else pd.DataFrame(columns=['timestamp', 'snr', 'constellation_type'])

def parse_location_file(loc_file_path):
    """Parse location data from CSV file."""
    try:
        # Read CSV file with comma separator and strip whitespace
        loc_df = pd.read_csv(loc_file_path, skipinitialspace=True)
        
        # Convert ISO timestamps to milliseconds since epoch
        loc_df['timestamp'] = pd.to_datetime(loc_df['timestamp']).astype(np.int64) // 10**6
        
        # Ensure column names match expected format
        loc_df = loc_df.rename(columns={
            'lat': 'latitude',
            'lon': 'longitude'
        })
        
        print("\nLocation data statistics:")
        print(f"Number of records: {len(loc_df)}")
        print("\nLatitude range:", loc_df['latitude'].min(), "to", loc_df['latitude'].max())
        print("Longitude range:", loc_df['longitude'].min(), "to", loc_df['longitude'].max())
        print("Height range:", loc_df['height'].min(), "to", loc_df['height'].max())
        
        return loc_df
        
    except Exception as e:
        print(f"Error parsing location file: {e}")
        return pd.DataFrame(columns=['timestamp', 'latitude', 'longitude', 'height'])

def find_closest_location(timestamp, loc_df, max_diff_ms=2000):
    """Find the closest location data to a given timestamp."""
    if loc_df.empty:
        return None, None, None
        
    time_diffs = abs(loc_df['timestamp'] - timestamp)
    closest_idx = time_diffs.idxmin()
    
    if time_diffs[closest_idx] <= max_diff_ms:
        row = loc_df.iloc[closest_idx]
        return row['latitude'], row['longitude'], row['height']
    return None, None, None

def process_files(agc_file_path, nmea_file_path, loc_file_path, output_file_path):
    """Process AGC, NMEA, and location files and generate merged output."""
    # Create empty DataFrame with correct columns
    empty_df = pd.DataFrame(columns=['timestamp', 'constellation', 'AGC', 'SNR', 'latitude', 'longitude', 'height'])
    
    # Parse input files
    agc_df = parse_agc_file(agc_file_path)
    nmea_df = parse_nmea_file(nmea_file_path)
    loc_df = parse_location_file(loc_file_path)
    
    if agc_df.empty or nmea_df.empty:
        print("Warning: One or both input files produced empty DataFrames")
        return empty_df
    
    # Print unique timestamps and constellation types for debugging
    print("\nUnique AGC timestamps:", agc_df['timestamp'].unique())
    print("Unique NMEA timestamps:", nmea_df['timestamp'].unique())
    print("\nUnique AGC constellation types:", agc_df['constellation_type'].unique())
    print("Unique NMEA constellation types:", nmea_df['constellation_type'].unique())
    
    # First, aggregate SNR values by timestamp and constellation
    snr_agg = nmea_df.groupby(['timestamp', 'constellation_type'], as_index=False).agg(
        SNR=('snr', 'mean'),
        satellite_count=('snr', 'count')
    )
    
    # For each NMEA record, find the previous matching AGC value
    matched_records = []
    for _, nmea_row in snr_agg.iterrows():
        # Find matching AGC record
        matching_agc = agc_df[
            (agc_df['constellation_type'] == nmea_row['constellation_type']) &
            (agc_df['timestamp'] <= nmea_row['timestamp'])
        ]
        
        if not matching_agc.empty:
            # Get the most recent AGC value
            agc_record = matching_agc.iloc[-1]
            
            # Find closest location data
            lat, lon, height = find_closest_location(nmea_row['timestamp'], loc_df)
            
            matched_records.append({
                'timestamp': nmea_row['timestamp'],  # Use NMEA timestamp as reference
                'constellation': CONSTELLATION_MAP[nmea_row['constellation_type']],
                'AGC': agc_record['agc'],
                'SNR': nmea_row['SNR'],
                'latitude': lat,
                'longitude': lon,
                'height': height
            })
    
    # Create output DataFrame
    output_df = pd.DataFrame(matched_records) if matched_records else empty_df
    
    if not output_df.empty:
        # Sort by timestamp and constellation
        output_df = output_df.sort_values(['timestamp', 'constellation'])
        
        # Save to CSV
        output_df.to_csv(output_file_path, index=False)
        print(f'\nOutput saved to {output_file_path}')
        
        # Display summary statistics
        print("\nSummary statistics:")
        print(f"Total records: {len(output_df)}")
        print("\nRecords per constellation:")
        print(output_df['constellation'].value_counts())
        print("\nSNR statistics:")
        print(output_df['SNR'].describe())
        print("\nAGC statistics:")
        print(output_df['AGC'].describe())
        if 'latitude' in output_df.columns:
            print("\nCoordinate statistics:")
            print("Latitude range:", output_df['latitude'].min(), "to", output_df['latitude'].max())
            print("Longitude range:", output_df['longitude'].min(), "to", output_df['longitude'].max())
            print("Height range:", output_df['height'].min(), "to", output_df['height'].max())
    else:
        print("\nNo matching records found")
    
    return output_df

if __name__ == "__main__":
    # Process the files
    process_files('agc.csv', 'gnss_log_2024_09_10_14_21_50.nmea', 'nmea.csv', 'output.csv')
