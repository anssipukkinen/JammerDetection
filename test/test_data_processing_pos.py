import unittest
from datetime import datetime
import pandas as pd
import numpy as np
from data.data_processing_pos_orig import (
    parse_agc_file,
    parse_nmea_file,
    parse_pos_file,
    process_files,
    find_closest_agc,
    CONSTELLATION_MAP,
    NMEA_TO_AGC_TYPE,
    is_valid_snr
)

class TestDataProcessing(unittest.TestCase):
    def setUp(self):
        self.agc_file = 'test/agc-test-data.csv'
        self.nmea_file = 'test/nmea-test-data.csv'
        self.pos_file = 'test/pos-sample-test.data'
        self.output_file = 'test/test_output.csv'

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
        self.assertEqual(first_row['constellation_type'], 5)  # GPS
        self.assertAlmostEqual(first_row['agc'], 61.720664978027344)
        
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

    def test_parse_pos_file(self):
        """Test position file parsing"""
        df = parse_pos_file(self.pos_file)
        
        # Check if DataFrame has expected columns
        expected_columns = {'timestamp', 'latitude', 'longitude', 'height', 'num_satellites'}
        self.assertEqual(set(df.columns), expected_columns)
        
        # Check if data is not empty
        self.assertGreater(len(df), 0)
        
        # Check if coordinates are in valid ranges
        self.assertTrue(all(-90 <= lat <= 90 for lat in df['latitude']))
        self.assertTrue(all(-180 <= lon <= 180 for lon in df['longitude']))
        
        # Check if timestamps are converted to milliseconds
        self.assertTrue(all(isinstance(ts, (int, np.int64)) for ts in df['timestamp']))
        
        # Check if number of satellites is valid (positive integer)
        self.assertTrue(all(isinstance(ns, (int, np.int64)) for ns in df['num_satellites']))
        self.assertTrue(all(ns > 0 for ns in df['num_satellites']))
        
        # Test specific timestamp conversion
        # First row from sample data: "2024/09/10 12:22:09.600"
        expected_timestamp = int(datetime.strptime("2024/09/10 12:22:09.600", 
                                                 "%Y/%m/%d %H:%M:%S.%f").timestamp() * 1000)
        self.assertEqual(df.iloc[0]['timestamp'], expected_timestamp)
        
        # Test specific coordinate values from sample data
        self.assertAlmostEqual(df.iloc[0]['latitude'], 69.212355629)
        self.assertAlmostEqual(df.iloc[0]['longitude'], 15.858570977)
        self.assertAlmostEqual(df.iloc[0]['height'], 59.9833)
        self.assertEqual(df.iloc[0]['num_satellites'], 13)
        
        # Test data consistency across multiple rows
        # Test that number of satellites changes correctly (from sample data)
        self.assertEqual(df.iloc[1]['num_satellites'], 16)  # Second row should have 16 satellites
        self.assertEqual(df.iloc[4]['num_satellites'], 17)  # Fifth row should have 17 satellites
        
        # Test timestamp continuity
        timestamps = df['timestamp'].values
        self.assertTrue(all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1)))
        
        # Verify total number of records matches expected length
        self.assertEqual(len(df), 124)  # Number of data rows in pos-sample-test.data

    def test_find_closest_agc(self):
        """Test finding closest AGC record"""
        # Create sample AGC DataFrame
        agc_data = {
            'timestamp': [1000, 2000, 3000],
            'agc': [30.0, 35.0, 40.0],
            'constellation_type': [1, 1, 1]  # GPS
        }
        agc_df = pd.DataFrame(agc_data)
        
        # Test exact match
        self.assertAlmostEqual(find_closest_agc(2000, 1, agc_df), 35.0)
        
        # Test closest match before
        self.assertAlmostEqual(find_closest_agc(2100, 1, agc_df), 35.0)
        
        # Test closest match after
        self.assertAlmostEqual(find_closest_agc(1900, 1, agc_df), 35.0)
        
        # Test no match within threshold (more than 2000ms away)
        self.assertIsNone(find_closest_agc(5500, 1, agc_df))
        
        # Test wrong constellation type
        self.assertIsNone(find_closest_agc(2000, 3, agc_df))  # GLONASS
        
        # Test empty DataFrame
        self.assertIsNone(find_closest_agc(2000, 1, pd.DataFrame()))

    def test_process_files(self):
        """Test complete file processing"""
        # Process the files
        output_df = process_files(self.agc_file, self.nmea_file, self.pos_file, self.output_file)
        
        # Check output format
        expected_columns = {'timestamp', 'constellation', 'AGC', 'SNR', 
                          'latitude', 'longitude', 'height', 'num_satellites'}
        self.assertEqual(set(output_df.columns), expected_columns)
        
        # Verify constellations are properly named
        valid_constellations = set(CONSTELLATION_MAP.values())
        self.assertTrue(all(c in valid_constellations for c in output_df['constellation'].unique()))
        
        # Check if some AGC values are present (not all need to have matches)
        self.assertTrue(any(pd.notna(output_df['AGC'])))
        
        # Check if all NMEA records are preserved (all should have valid SNR)
        self.assertTrue(all(pd.notna(output_df['SNR'])))
        self.assertTrue(all(is_valid_snr(snr) for snr in output_df['SNR']))
        
        # Verify AGC values are within reasonable range when present
        valid_agc = output_df[pd.notna(output_df['AGC'])]['AGC']
        self.assertTrue(all(-100 <= agc <= 100 for agc in valid_agc))  # Assuming reasonable AGC range
        
        # Check if coordinates are in valid ranges when present
        valid_lat = output_df[pd.notna(output_df['latitude'])]['latitude']
        valid_lon = output_df[pd.notna(output_df['longitude'])]['longitude']
        self.assertTrue(all(-90 <= lat <= 90 for lat in valid_lat))
        self.assertTrue(all(-180 <= lon <= 180 for lon in valid_lon))
        
        # Check if number of satellites is valid when present
        valid_sats = output_df[pd.notna(output_df['num_satellites'])]['num_satellites']
        self.assertTrue(all(isinstance(ns, (int, np.int64)) for ns in valid_sats))
        self.assertTrue(all(ns > 0 for ns in valid_sats))
        
        # Verify timestamps are sorted
        self.assertTrue(output_df['timestamp'].is_monotonic_increasing)

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
