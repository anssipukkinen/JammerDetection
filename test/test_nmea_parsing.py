import unittest
import pandas as pd
from data.data_processing_pos import parse_nmea_file, CONSTELLATION_MAP, NMEA_TO_AGC_TYPE

class TestNMEAParsing(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test/test_NMEA_GPGSV_Galileo.csv'

    def test_parse_nmea_file(self):
        """Test NMEA file parsing with GPS messages."""
        # First, let's analyze a single line manually
        test_line = "NMEA,$GPGSV,5,1,14,09,69,147,45,04,43,096,31,11,43,264,41,20,39,289,41*7F,1725970940551"
        parts = test_line.split(',')
        print("\nAnalyzing GPGSV message structure:")
        print(f"Total parts: {len(parts)}")
        for i, part in enumerate(parts):
            print(f"Index {i}: {part}")
        
        print("\nExpected satellite blocks:")
        # First block: 09,69,147,45
        print("Block 1:", parts[4:8])
        # Second block: 04,43,096,31
        print("Block 2:", parts[8:12])
        # Third block: 11,43,264,41
        print("Block 3:", parts[12:16])
        # Fourth block: 20,39,289,41
        print("Block 4:", parts[16:20])
        
        # Now parse the actual file
        df = parse_nmea_file(self.test_file)
        
        print("\nDebug Information:")
        print("DataFrame contents:")
        print(df)
        print("\nUnique constellation types:", df['constellation_type'].unique())
        print("\nSNR values by timestamp:")
        for ts in df['timestamp'].unique():
            snr_values = df[df['timestamp'] == ts]['snr'].tolist()
            print(f"Timestamp {ts}: SNR values = {snr_values}")
        
        # Check if DataFrame has expected columns
        expected_columns = {'timestamp', 'snr', 'constellation_type'}
        self.assertEqual(set(df.columns), expected_columns)
        
        # Check if data is not empty
        self.assertGreater(len(df), 0)
        
        # Verify constellation type is GPS (1)
        unique_constellations = df['constellation_type'].unique()
        self.assertEqual(len(unique_constellations), 1)
        self.assertEqual(unique_constellations[0], 1)  # GPS type
        
        # Group by timestamp and verify average SNR values
        avg_snr = df.groupby('timestamp')['snr'].mean()
        
        # Expected values from our previous test
        expected_values = {
            1725970940551: 37.777777777778,  # (45+31+41+41+34+39+38+41+30)/9
            1725970940552: 38.0,             # (44+41+27+40+38)/5
            1725970941535: 37.928571428571430  # (45+32+41+41+34+39+38+41+30+44+41+27+40+38)/14
        }
        
        print("\nAverage SNR by timestamp:")
        for timestamp, expected_snr in expected_values.items():
            actual_snr = avg_snr[timestamp]
            print(f"Timestamp {timestamp}:")
            print(f"  Expected SNR: {expected_snr}")
            print(f"  Actual SNR: {actual_snr}")
            self.assertAlmostEqual(actual_snr, expected_snr, places=4,
                                 msg=f"For timestamp {timestamp}, expected SNR {expected_snr}, but got {actual_snr}")

if __name__ == '__main__':
    unittest.main()
