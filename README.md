# GNSS Jammer Detection

This project implements a system for detecting GNSS (Global Navigation Satellite System) jamming events using machine learning techniques and various data sources.

## Project Structure

- `data/`: Contains data processing scripts and datasets
  - `source/`: Raw data files (NMEA, POS, AGC logs)
  - `data_processing_pos.py`: Source data matching (combines files based on timestamp). Creates file `output_all_pos.csv` which was edited manually in Excel by adding legitimate/jammed classes and saved as `manual_data_with_classes.csv`
  - `pre-processor.py`: Data preprocessing (normalisation, dropping BeiDou records and applying median for missing AGC values) for `manual_data_with_classes.csv`
- `model/`: Machine learning models
  - `random_forest.py`: Takes `manual_data_with_classes.csv` as input and implements Random Forest classifier
- `test/`: Test files for data processing and test data
- `visualisation/`: Data visualization for combined data file
  - `folium_map.py`: Map-based interactive visualization using Folium

## Data Sources

The system utilizes multiple data sources:
- GNSS position data (POS format)
- NMEA messages
- Automatic Gain Control (AGC) values

## Installation

1. Clone this repository
2. Install required Python packages:
```bash
pip install numpy pandas scikit-learn folium
```

## Usage

1. Place your GNSS log files in the `data/source/` directory
2. Merge source data files with `data_processing_pos.py`
3. Run data merging tests
```bash
PYTHONPATH=. python test/test_data_processing_pos.py -v
```
4. Visualize results by creating html map file: 
```bash
python visualisation/folium_map.py
```
5. Open file `animated_map_with_agc_snr_all_data2.html` in browser (tested with Chrome)
6. Label output data file with classes (e.g. in Excel) or use pre-labelled data file (`manual_data_with_classes.csv`)
7. Preprocess the data:
```bash
python data/pre-processor.py
```
8. Run the jammer detection model:
```bash
python model/random_forest.py
```

## Key Components

### Data Processing
- Position data processing (`data_processing_pos.py`)
- Data preprocessing and feature extraction (`pre-processor.py`)

### Machine Learning
- Random Forest classifier for jammer detection
- Feature engineering based on GNSS signals and AGC values

### Visualization
- Interactive map visualization using Folium

