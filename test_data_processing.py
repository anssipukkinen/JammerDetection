import unittest
from datetime import datetime
import pandas as pd
import numpy as np
from data_processing import (
    parse_agc_file,
    parse_nmea_file,
    parse_location_file,
    process_files,
    CONSTELLATION_MAP,
    NMEA_TO_AGC_TYPE,
    is_valid_snr
)

class TestDataProcessing(unittest.TestCase):
    def setUp(self):
        self.agc_file = 'agc-test-data.csv'
        self.nmea_file = 'nmea-test-data.csv'
        self.loc_file = 'nmea-loc-test.csv'
        self.output_file = 'test_output.csv'

    def test_parse_agc_file(self):
        """Test AGC file parsing"""
        df = parse_agc_file(self.agc_file)
        
        # Check if DataFrame has expected columns
        expected_columns = {'timestamp', 'agc', 'constellation_type'}
        self.assertEqual(set(df.columns), expected_columns)
        
        # Check if data is not empty
        self.assertGreater(len(df), 0)
        
        # Verify first row values from sample data
        first_row = df.iloc[0]
        self.assertEqual(first_row['constellation_type'], 1)  # GPS
        self.assertAlmostEqual(first_row['agc'], 39.776634216308594)
        
        # Check if all constellation types are valid
        valid_types = set(CONSTELLATION_MAP.keys())
        self.assertTrue(all(ct in valid_types for ct in df['constellation_type'].unique()))

    def test_parse_nmea_file(self):
        """Test NMEA file parsing"""
        df = parse_nmea_file(self.nmea_file)
        
        # Check if DataFrame has expected columns
        expected_columns = {'timestamp', 'snr', 'constellation_type'}
        self.assertEqual(set(df.columns), expected_columns)
        
        # Check if data is not empty
        self.assertGreater(len(df), 0)
        
        # Verify constellation types are mapped correctly
        valid_types = set(CONSTELLATION_MAP.keys())
        self.assertTrue(all(ct in valid_types for ct in df['constellation_type'].unique()))
        
        # Check if all SNR values are valid
        self.assertTrue(all(is_valid_snr(snr) for snr in df['snr']))
        
        # Verify we have data for different constellations
        self.assertGreater(len(df['constellation_type'].unique()), 1)

    def test_parse_location_file(self):
        """Test location file parsing"""
        df = parse_location_file(self.loc_file)
        
        # Check if DataFrame has expected columns
        expected_columns = {'timestamp', 'latitude', 'longitude', 'height'}
        self.assertEqual(set(df.columns), expected_columns)
        
        # Check if data is not empty
        self.assertGreater(len(df), 0)
        
        # Check if coordinates are in valid ranges
        self.assertTrue(all(-90 <= lat <= 90 for lat in df['latitude']))
        self.assertTrue(all(-180 <= lon <= 180 for lon in df['longitude']))
        
        # Check if timestamps are converted to milliseconds
        self.assertTrue(all(isinstance(ts, (int, np.int64)) for ts in df['timestamp']))

    def test_process_files(self):
        """Test complete file processing"""
        # Process the files
        output_df = process_files(self.agc_file, self.nmea_file, self.loc_file, self.output_file)
        
        # Check output format
        expected_columns = {'timestamp', 'constellation', 'AGC', 'SNR', 'latitude', 'longitude', 'height'}
        self.assertEqual(set(output_df.columns), expected_columns)
        
        # Verify constellations are properly named
        valid_constellations = set(CONSTELLATION_MAP.values())
        self.assertTrue(all(c in valid_constellations for c in output_df['constellation'].unique()))
        
        # Check if AGC values are present
        self.assertTrue(any(pd.notna(output_df['AGC'])))
        
        # Check if SNR values are valid when present
        valid_snr = output_df[pd.notna(output_df['SNR'])]['SNR']
        self.assertTrue(all(is_valid_snr(snr) for snr in valid_snr))
        
        # Check if coordinates are in valid ranges when present
        if 'latitude' in output_df.columns:
            valid_lat = output_df[pd.notna(output_df['latitude'])]['latitude']
            valid_lon = output_df[pd.notna(output_df['longitude'])]['longitude']
            self.assertTrue(all(-90 <= lat <= 90 for lat in valid_lat))
            self.assertTrue(all(-180 <= lon <= 180 for lon in valid_lon))

    def test_constellation_mapping(self):
        """Test constellation mapping consistency"""
        # Test NMEA to AGC type mapping
        for nmea_prefix, agc_type in NMEA_TO_AGC_TYPE.items():
            self.assertIn(agc_type, CONSTELLATION_MAP)
            
        # Test all constellation types have mappings
        for agc_type in CONSTELLATION_MAP:
            self.assertTrue(any(t == agc_type for t in NMEA_TO_AGC_TYPE.values()))

    def test_snr_validation(self):
        """Test SNR validation function"""
        # Test valid SNR values
        self.assertTrue(is_valid_snr(0))
        self.assertTrue(is_valid_snr(50))
        self.assertTrue(is_valid_snr(99))
        
        # Test invalid SNR values
        self.assertFalse(is_valid_snr(-1))
        self.assertFalse(is_valid_snr(100))
        self.assertFalse(is_valid_snr('invalid'))
        self.assertFalse(is_valid_snr(None))

if __name__ == '__main__':
    unittest.main()
