import pandas as pd
import re
import sys
import numpy as np
from datetime import datetime, timezone

# [Previous code remains the same until find_closest_location function]

def find_closest_location(timestamp, loc_df, max_diff_ms=2000):
    """Find the closest location data to a given timestamp."""
    if loc_df.empty:
        return None, None, None, None
        
    time_diffs = abs(loc_df['timestamp'] - timestamp)
    closest_idx = time_diffs.idxmin()
    min_diff = time_diffs[closest_idx]
    
    # Debug output for first few timestamps
    if timestamp < 1725970928548:  # Before first successful match
        print(f"\nLooking for location at {format_timestamp(timestamp)}")
        print(f"Closest location is at {format_timestamp(loc_df.iloc[closest_idx]['timestamp'])}")
        print(f"Time difference: {min_diff/1000:.3f} seconds")
    
    if min_diff <= max_diff_ms:
        row = loc_df.iloc[closest_idx]
        return row['latitude'], row['longitude'], row['height'], int(row['num_satellites'])
    return None, None, None, None

# [Rest of the code remains the same]
