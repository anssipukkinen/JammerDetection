import pandas as pd

def filter_constellations(input_file):
    # Read the input file with semicolon separator
    df = pd.read_csv(input_file, sep=';')
    
    # List of constellations to filter
    constellations = ['GPS', 'Galileo', 'GLONASS', 'BeiDou']
    
    # Create separate files for each constellation
    for constellation in constellations:
        # Filter rows for current constellation
        constellation_df = df[df['constellation'] == constellation]
        
        # Save to output file
        output_file = f'data/output_{constellation.lower()}.csv'
        constellation_df.to_csv(output_file, sep=';', index=False)
        print(f"Created {output_file}")

if __name__ == "__main__":
    input_file = 'data/manual_data_with_classes.csv'
    filter_constellations(input_file)
