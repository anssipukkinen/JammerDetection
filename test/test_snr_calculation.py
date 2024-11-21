import unittest
import pandas as pd
import numpy as np

class TestSNRCalculation(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test/test_NMEA_GPGSV_Galileo.csv'

    def extract_snr_data(self, gpgsv_line):
        """Extract SNR values and timestamp from a GPGSV message."""
        parts = gpgsv_line.split(',')
        snr_values = []
        
        # Get timestamp from the last field
        timestamp = int(parts[-1])
        
        # Each satellite block has 4 fields: PRN, elevation, azimuth, SNR
        # Starting from index 4 (first satellite block), step by 4 to get each block
        for i in range(4, len(parts)-1, 4):
            try:
                # Get the SNR value (last field in each block)
                if i+3 >= len(parts)-1:  # -1 to exclude timestamp field
                    break
                    
                # Handle the last value which might contain checksum
                if '*' in parts[i+3]:
                    snr = parts[i+3].split('*')[0]
                else:
                    snr = parts[i+3]
                
                if snr.strip():  # Check if SNR value exists
                    snr_value = int(snr)
                    snr_values.append((timestamp, snr_value))
            except (ValueError, IndexError):
                continue
        
        return snr_values

    def calculate_average_snr_by_timestamp(self, file_path):
        """Calculate average SNR grouped by timestamp from GPGSV messages."""
        snr_data = []
        
        with open(file_path, 'r') as file:
            for line in file:
                if "$GPGSV" in line:
                    values = self.extract_snr_data(line)
                    snr_data.extend(values)
        
        # Convert to DataFrame for easier grouping
        df = pd.DataFrame(snr_data, columns=['timestamp', 'snr'])
        
        # Group by timestamp and calculate mean
        avg_snr = df.groupby('timestamp')['snr'].mean().reset_index()
        return avg_snr.sort_values('timestamp')

    def test_extract_snr_single_line(self):
        """Test SNR extraction from a single GPGSV line."""
        test_line = "$GPGSV,5,1,14,09,69,147,45,04,43,096,32,11,43,264,41,20,39,289,41*7C,1725970941535"
        snr_data = self.extract_snr_data(test_line)
        expected_timestamp = 1725970941535
        expected_values = [(expected_timestamp, 45), (expected_timestamp, 32), 
                         (expected_timestamp, 41), (expected_timestamp, 41)]
        self.assertEqual(snr_data, expected_values, 
                        f"Expected SNR data {expected_values}, but got {snr_data}")

    def test_extract_snr_with_missing_values(self):
        """Test SNR extraction when some values are missing."""
        test_line = "$GPGSV,5,4,14,09,,,44,04,,,41,11,,,27,26,,,40,8*64,1725970941535"
        snr_data = self.extract_snr_data(test_line)
        expected_timestamp = 1725970941535
        expected_values = [(expected_timestamp, 44), (expected_timestamp, 41),
                         (expected_timestamp, 27), (expected_timestamp, 40)]
        self.assertEqual(snr_data, expected_values,
                        f"Expected SNR data {expected_values}, but got {snr_data}")

    def test_average_snr_by_timestamp(self):
        """Test average SNR calculation grouped by timestamp."""
        avg_snr_df = self.calculate_average_snr_by_timestamp(self.test_file)
        
        # Verify DataFrame structure
        self.assertIn('timestamp', avg_snr_df.columns)
        self.assertIn('snr', avg_snr_df.columns)
        
        # Verify we have exactly three rows (one for each unique timestamp)
        self.assertEqual(len(avg_snr_df), 3)
        
        # Expected values for each timestamp
        expected_values = {
            1725970940551: 37.777777777777778,  # (45+31+41+41+34+39+38+41+30)/9
            1725970940552: 38.0,                # (44+41+27+40+38)/5
            1725970941535: 37.928571428571430   # (45+32+41+41+34+39+38+41+30+44+41+27+40+38)/14
        }
        
        # Verify values for each timestamp
        for _, row in avg_snr_df.iterrows():
            timestamp = row['timestamp']
            actual_snr = row['snr']
            expected_snr = expected_values[timestamp]
            
            self.assertAlmostEqual(actual_snr, expected_snr, places=4,
                                 msg=f"For timestamp {timestamp}, expected SNR {expected_snr}, but got {actual_snr}")

    def test_empty_file_handling(self):
        """Test handling of empty or invalid files."""
        # Create a temporary empty file for testing
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("")
            temp_path = temp_file.name

        avg_snr_df = self.calculate_average_snr_by_timestamp(temp_path)
        self.assertTrue(avg_snr_df.empty,
                       "Expected empty DataFrame for empty file")

        # Clean up
        import os
        os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()
