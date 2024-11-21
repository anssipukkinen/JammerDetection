def filter_gpgsv_sentences(input_file, output_file):
    """
    Filter NMEA data to extract only $GPGSV sentences.
    
    Parameters:
    input_file (str): Path to input NMEA file
    output_file (str): Path to save filtered sentences
    """
    try:
        # Read input file and filter GPGSV sentences
        with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
            for line in f_in:
                # Clean the line and split by comma
                parts = line.strip().split(',')
                
                # Check if it's a valid NMEA line and contains GPGSV
                if len(parts) > 1 and '$GPGSV' in parts[1]:
                    # Extract the NMEA sentence (everything after "NMEA,")
                    nmea_sentence = ','.join(parts[1:])
                    f_out.write(nmea_sentence + '\n')
        
        print(f"Filtered GPGSV sentences saved to {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def parse_gpgsv_sentence(sentence):
    """
    Parse a GPGSV sentence into its components.
    
    GPGSV format:
    $GPGSV,<total messages>,<message number>,<satellites in view>,
    [<satellite ID>,<elevation>,<azimuth>,<SNR>,...] (repeated up to 4 times)
    
    Parameters:
    sentence (str): GPGSV NMEA sentence
    
    Returns:
    dict: Parsed sentence components
    """
    try:
        # Remove checksum
        sentence = sentence.split('*')[0]
        
        # Split the sentence into fields
        fields = sentence.split(',')
        
        # Basic sentence information
        data = {
            'total_messages': int(fields[1]),
            'message_number': int(fields[2]),
            'satellites_in_view': int(fields[3])
        }
        
        # Parse satellite information (up to 4 satellites per sentence)
        satellites = []
        for i in range(0, min(4, (len(fields) - 4) // 4)):
            base_idx = 4 + (i * 4)
            if base_idx + 3 < len(fields):
                satellite = {
                    'satellite_id': fields[base_idx],
                    'elevation': fields[base_idx + 1],
                    'azimuth': fields[base_idx + 2],
                    'snr': fields[base_idx + 3]
                }
                satellites.append(satellite)
        
        data['satellites'] = satellites
        return data
        
    except Exception as e:
        print(f"Error parsing GPGSV sentence: {str(e)}")
        return None

if __name__ == "__main__":
    input_file = "data/source/gnss_log_2024_09_10_14_21_50.nmea"
    output_file = "data/source/gpgsv_filtered.nmea"
    filter_gpgsv_sentences(input_file, output_file)
    
    # Example of parsing first sentence from output
    try:
        with open(output_file, 'r') as f:
            first_sentence = f.readline().strip()
            if first_sentence:
                parsed_data = parse_gpgsv_sentence(first_sentence)
                print("\nExample parsed GPGSV sentence:")
                print(parsed_data)
    except Exception as e:
        print(f"Error reading output file: {str(e)}")
