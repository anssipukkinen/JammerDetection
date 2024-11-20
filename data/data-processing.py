import pandas as pd
from datetime import datetime
import re

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
    'GB': 7,  # BeiDou
    'BD': 7   # Alternative BeiDou prefix
}

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
                    
                    agc_data.append({
                        'timestamp': datetime.fromtimestamp(timestamp/1000.0),
                        'agc': agc_db,
                        'constellation_type': constellation_type
                    })
                except (IndexError, ValueError) as e:
                    continue
                    
    return pd.DataFrame(agc_data)

def parse_nmea_file(nmea_file_path):
    """Parse NMEA data focusing on GSV sentences for SNR."""
    nmea_data = []
    current_timestamp = None
    
    with open(nmea_file_path, 'r') as file:
        for line in file:
            if not line.startswith('NMEA,$'):
                continue
                
            # Extract timestamp from the end of the line
            timestamp_match = re.search(r',(\d+)$', line)
            if timestamp_match:
                current_timestamp = int(timestamp_match.group(1))
            
            parts = line.strip().split(',')
            sentence = parts[1]
            
            # Handle GSV sentences for SNR data
            if sentence.endswith('GSV'):
                constellation_prefix = sentence[:2]
                if constellation_prefix in NMEA_TO_AGC_TYPE:
                    constellation_type = NMEA_TO_AGC_TYPE[constellation_prefix]
                    
                    # Process satellite information
                    for i in range(4, len(parts)-4, 4):  # -4 to account for checksum and timestamp
                        try:
                            if len(parts) > i+3 and parts[i+3] and parts[i+3] != '*':
                                snr = int(parts[i+3])
                                nmea_data.append({
                                    'timestamp': datetime.fromtimestamp(current_timestamp/1000.0),
                                    'snr': snr,
                                    'constellation_type': constellation_type
                                })
                        except (ValueError, IndexError):
                            continue
                            
    return pd.DataFrame(nmea_data)

def process_files(agc_file_path, nmea_file_path, output_file_path):
    """Process AGC and NMEA files and generate merged output."""
    # Parse input files
    agc_df = parse_agc_file(agc_file_path)
    nmea_df = parse_nmea_file(nmea_file_path)
    
    # Round timestamps to nearest second for matching
    agc_df['timestamp_rounded'] = agc_df['timestamp'].dt.round('1s')
    nmea_df['timestamp_rounded'] = nmea_df['timestamp'].dt.round('1s')
    
    # Aggregate SNR values by constellation and timestamp
    snr_agg = nmea_df.groupby(['timestamp_rounded', 'constellation_type'])['snr'].agg(['mean', 'count']).reset_index()
    snr_agg.columns = ['timestamp_rounded', 'constellation_type', 'snr_mean', 'satellite_count']
    
    # Merge AGC and SNR data
    merged_df = pd.merge(
        agc_df,
        snr_agg,
        on=['timestamp_rounded', 'constellation_type'],
        how='left'
    )
    
    # Add constellation names
    merged_df['constellation'] = merged_df['constellation_type'].map(CONSTELLATION_MAP)
    
    # Clean up and prepare final output
    output_df = merged_df[[
        'timestamp',
        'constellation',
        'agc',
        'snr_mean'
    ]].rename(columns={
        'agc': 'AGC',
        'snr_mean': 'SNR'
    })
    
    # Sort by timestamp and constellation
    output_df = output_df.sort_values(['timestamp', 'constellation'])
    
    # Save to CSV
    output_df.to_csv(output_file_path, index=False)
    print(f'Output saved to {output_file_path}')
    
    # Display summary statistics
    print("\nSummary statistics:")
    print(f"Total records: {len(output_df)}")
    print("\nRecords per constellation:")
    print(output_df['constellation'].value_counts())

if __name__ == "__main__":
    # Process the files
    process_files('agc-test-data.csv', 'nmea-test-data.csv', 'output.csv')
