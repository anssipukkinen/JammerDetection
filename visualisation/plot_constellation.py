import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def plot_constellation_attribute(file_path, attribute):
    """
    Plot time series of selected attribute from constellation data file.
    
    Parameters:
    file_path (str): Path to the constellation CSV file
    attribute (str): Column name to plot (e.g., 'AGC', 'SNR', 'height')
    """
    # Read the CSV file
    df = pd.read_csv(file_path, sep=';')
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Plot the attribute over time
    plt.plot(df['timestamp'], df[attribute], 'b-', label=attribute)
    
    # Color points by class if it exists
    if 'class' in df.columns:
        jammed_mask = df['class'] == 'jammed'
        plt.scatter(df[jammed_mask]['timestamp'], df[jammed_mask][attribute], 
                   color='red', label='Jammed', alpha=0.6)
        plt.scatter(df[~jammed_mask]['timestamp'], df[~jammed_mask][attribute], 
                   color='green', label='Legitimate', alpha=0.6)
    
    # Get constellation name from file path
    constellation = file_path.split('_')[-1].split('.')[0].upper()
    
    # Set title and labels
    plt.title(f'{attribute} over Time for {constellation} Constellation')
    plt.xlabel('Time')
    plt.ylabel(attribute)
    plt.legend()
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Example usage
    file_path = "data/output_beidou.csv"
    plot_constellation_attribute(file_path, "SNR")
