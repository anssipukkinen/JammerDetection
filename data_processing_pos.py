import pandas as pd
import re
import numpy as np
from datetime import datetime, timezone

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

def gpst_to_unix(gpst_str):
    """Convert GPS Time string to Unix timestamp in milliseconds."""
    # Parse the date and time without timezone info to match test expectations
    dt = datetime.strptime(gpst_str, "%Y/%m/%d %H:%M:%S.%f")
    # Convert to milliseconds
    return int(dt.timestamp() * 1000)

def parse_pos_file(pos_file_path):
    """Parse position data from .dat file."""
    pos_data = []
    
    with open(pos_file_path, 'r') as file:
        # Skip header lines (first 14 lines)
        for _ in range(14):
            next(file)
            
        for line in file:
            try:
                parts = line.strip().split()
                if len(parts) >= 8:  # Ensure we have at least the required columns
                    # Parse timestamp
                    date_str = f"{parts[0]} {parts[1]}"
                    timestamp = gpst_to_unix(date_str)
                    
                    # Extract coordinates and number of satellites
                    latitude = float(parts[2])
                    longitude = float(parts[3])
                    height = float(parts[4])
                    num_satellites = int(parts[6])
                    
                    pos_data.append({
                        'timestamp': timestamp,
                        'latitude': latitude,
                        'longitude': longitude,
                        'height': height,
                        'num_satellites': num_satellites
                    })
            except (ValueError, IndexError) as e:
                print(f"Error parsing line: {line.strip()}")
                continue
    
    df = pd.DataFrame(pos_data)
    if not df.empty:
        print("\nPosition data statistics:")
        print(f"Number of records: {len(df)}")
        print("\nLatitude range:", df['latitude'].min(), "to", df['latitude'].max())
        print("Longitude range:", df['longitude'].min(), "to", df['longitude'].max())
        print("Height range:", df['height'].min(), "to", df['height'].max())
        print("Satellites range:", df['num_satellites'].min(), "to", df['num_satellites'].max())
        print("\nTimestamp range:")
        print("Start:", datetime.fromtimestamp(df['timestamp'].min()/1000))
        print("End:", datetime.fromtimestamp(df['timestamp'].max()/1000))
    
    return df

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
        print("Start:", datetime.fromtimestamp(df['timestamp'].min()/1000))
        print("End:", datetime.fromtimestamp(df['timestamp'].max()/1000))
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
        print("Start:", datetime.fromtimestamp(df['timestamp'].min()/1000))
        print("End:", datetime.fromtimestamp(df['timestamp'].max()/1000))
        print("\nSNR value statistics:")
        print(df['snr'].describe())
    return df if not df.empty else pd.DataFrame(columns=['timestamp', 'snr', 'constellation_type'])

def find_closest_location(timestamp, loc_df, max_diff_ms=2000):
    """Find the closest location data to a given timestamp."""
    if loc_df.empty:
        return None, None, None, None
        
    time_diffs = abs(loc_df['timestamp'] - timestamp)
    closest_idx = time_diffs.idxmin()
    min_diff = time_diffs[closest_idx]
    
    if min_diff <= max_diff_ms:
        row = loc_df.iloc[closest_idx]
        return row['latitude'], row['longitude'], row['height'], int(row['num_satellites'])
    return None, None, None, None

def find_closest_agc(timestamp, constellation_type, agc_df, max_diff_ms=2000):
    """Find the closest AGC record to a given timestamp for a specific constellation."""
    if agc_df.empty:
        return None
    
    # Filter AGC records for the specific constellation
    constellation_agc = agc_df[agc_df['constellation_type'] == constellation_type]
    
    if constellation_agc.empty:
        return None
    
    # Calculate absolute time differences
    time_diffs = abs(constellation_agc['timestamp'] - timestamp)
    min_diff = time_diffs.min()
    
    # Check if the minimum time difference exceeds the threshold
    if min_diff >= max_diff_ms:
        return None
        
    # Get the closest record within threshold
    closest_idx = time_diffs.idxmin()
    return constellation_agc.loc[closest_idx, 'agc']

def process_files(agc_file_path, nmea_file_path, pos_file_path, output_file_path):
    """Process AGC, NMEA, and position files and generate merged output."""
    # Create empty DataFrame with correct columns
    empty_df = pd.DataFrame(columns=['timestamp', 'constellation', 'AGC', 'SNR', 'latitude', 'longitude', 'height', 'num_satellites'])
    
    # Parse input files
    agc_df = parse_agc_file(agc_file_path)
    nmea_df = parse_nmea_file(nmea_file_path)
    loc_df = parse_pos_file(pos_file_path)
    
    if nmea_df.empty:
        print("Warning: NMEA file produced empty DataFrame")
        return empty_df
    
    # Print unique timestamps and constellation types for debugging
    print("\nUnique AGC timestamps:", agc_df['timestamp'].unique() if not agc_df.empty else "No AGC data")
    print("Unique NMEA timestamps:", nmea_df['timestamp'].unique())
    print("\nUnique AGC constellation types:", agc_df['constellation_type'].unique() if not agc_df.empty else "No AGC data")
    print("Unique NMEA constellation types:", nmea_df['constellation_type'].unique())
    
    # First, aggregate SNR values by timestamp and constellation
    snr_agg = nmea_df.groupby(['timestamp', 'constellation_type'], as_index=False).agg(
        SNR=('snr', 'mean')
    )
    
    # For each unique timestamp, find the closest location data first
    unique_timestamps = snr_agg['timestamp'].unique()
    location_matches = {}
    for ts in unique_timestamps:
        lat, lon, height, num_sats = find_closest_location(ts, loc_df)
        location_matches[ts] = {
            'latitude': lat,
            'longitude': lon,
            'height': height,
            'num_satellites': int(num_sats) if num_sats is not None else None
        }
    
    # For each NMEA record, combine with location data and find AGC value
    matched_records = []
    for _, nmea_row in snr_agg.iterrows():
        # Get location data for this timestamp
        loc_data = location_matches[nmea_row['timestamp']]
        
        # Find closest AGC record
        agc_value = find_closest_agc(nmea_row['timestamp'], nmea_row['constellation_type'], agc_df)
        
        # Create record with all available data
        matched_records.append({
            'timestamp': nmea_row['timestamp'],
            'constellation': CONSTELLATION_MAP[nmea_row['constellation_type']],
            'AGC': agc_value,
            'SNR': nmea_row['SNR'],
            'latitude': loc_data['latitude'],
            'longitude': loc_data['longitude'],
            'height': loc_data['height'],
            'num_satellites': int(loc_data['num_satellites']) if loc_data['num_satellites'] is not None else None
        })
    
    # Create output DataFrame
    output_df = pd.DataFrame(matched_records) if matched_records else empty_df
    
    if not output_df.empty:
        # Sort by timestamp and constellation
        output_df = output_df.sort_values(['timestamp', 'constellation'])
        
        # Save to CSV with proper formatting
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
        
        # Print coordinate statistics only for valid coordinates
        valid_coords = output_df.dropna(subset=['latitude', 'longitude', 'height', 'num_satellites'])
        if not valid_coords.empty:
            print("\nCoordinate statistics:")
            print("Latitude range:", valid_coords['latitude'].min(), "to", valid_coords['latitude'].max())
            print("Longitude range:", valid_coords['longitude'].min(), "to", valid_coords['longitude'].max())
            print("Height range:", valid_coords['height'].min(), "to", valid_coords['height'].max())
            print("Number of satellites range:", valid_coords['num_satellites'].min(), "to", valid_coords['num_satellites'].max())
    else:
        print("\nNo matching records found")
    
    return output_df

if __name__ == "__main__":
    # Process the files
    process_files('agc.csv', 'gnss_log_2024_09_10_14_21_50.nmea', 'gnss_log_2024_09_10_14_21_50.pos', 'output_all_pos.csv')
