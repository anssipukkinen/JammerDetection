import folium
from folium.plugins import TimestampedGeoJson
import pandas as pd
import json
import branca.colormap as cm
import numpy as np

# Create DataFrame
df = pd.read_csv('output_all_pos.csv')

# Filter out rows with NaN coordinates
df_valid = df.dropna(subset=['latitude', 'longitude'])

# Check if we have any valid coordinates
if len(df_valid) == 0:
    raise ValueError("No valid coordinates found in the dataset")

# Normalize SNR for marker size scaling
snr_min = df['SNR'].min()
snr_max = df['SNR'].max()
df['SNR_normalized'] = (df['SNR'] - snr_min) / (snr_max - snr_min)

# Convert timestamp to ISO format
df['time'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%dT%H:%M:%SZ')

# Get min and max AGC values, excluding NaN/None
agc_min = df['AGC'].dropna().min()
agc_max = df['AGC'].dropna().max()

# Create a colormap for AGC values
colormap = cm.LinearColormap(
    colors=['blue', 'red'],
    vmin=agc_min,
    vmax=agc_max,
    caption='AGC Value'
)

# Create GeoJSON features
features = []
for idx, row in df.iterrows():
    # Skip points with invalid coordinates
    if pd.isna(row['latitude']) or pd.isna(row['longitude']):
        continue
        
    # Create tooltip content with conditional AGC formatting
    agc_text = f"{row['AGC']:.2f}" if pd.notna(row['AGC']) else "No data"
    tooltip_content = (
        f"Time: {row['time']}<br>"
        f"Constellation: {row['constellation']}<br>"
        f"AGC: {agc_text}<br>"
        f"SNR: {row['SNR']:.2f}<br>"
        f"Lat: {row['latitude']:.6f}<br>"
        f"Lon: {row['longitude']:.6f}<br>"
        f"Height: {row['height']:.2f}"
    )
    
    # Set default color for missing AGC values
    if pd.isna(row['AGC']):
        fill_color = 'gray'  # Use gray for missing AGC values
    else:
        fill_color = colormap(row['AGC'])
    
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [row['longitude'], row['latitude']],
        },
        'properties': {
            'time': row['time'],
            'icon': 'circle',
            'iconstyle': {
                'fillColor': fill_color,
                'fillOpacity': 0.6,
                'stroke': 'true',
                'radius': 5 + row['SNR_normalized'] * 10
            },
            'style': {'color': fill_color},
            'tooltip': tooltip_content,
            'permanent': True
        }
    }
    features.append(feature)

# Create GeoJSON
geojson = {
    'type': 'FeatureCollection',
    'features': features
}

# Initialize map with mean of valid coordinates
m = folium.Map(location=[df_valid['latitude'].mean(), df_valid['longitude'].mean()], zoom_start=10)

# Add TimestampedGeoJson with speed control
timestamped = TimestampedGeoJson(
    data=json.dumps(geojson),
    period='PT1S',
    duration='PT1S',
    transition_time=200,
    auto_play=True,
    loop=False,
    max_speed=10,
    loop_button=True,
    time_slider_drag_update=True,
    add_last_point=True
)

timestamped.add_to(m)

# Add colormap to map
colormap.add_to(m)

# Save map to HTML
m.save('animated_map_with_agc_snr_all_data2.html')

# Add custom CSS to the saved file to style tooltips
with open('animated_map_with_agc_snr_all_data2.html', 'r') as file:
    content = file.read()

css = """
<style>
.leaflet-tooltip {
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 5px;
    font-family: Arial, sans-serif;
    font-size: 12px;
    white-space: nowrap;
}
.leaflet-tooltip-top:before,
.leaflet-tooltip-bottom:before,
.leaflet-tooltip-left:before,
.leaflet-tooltip-right:before {
    display: none;
}
</style>
"""

# Insert CSS into head section
content = content.replace('</head>', f'{css}</head>')

with open('animated_map_with_agc_snr_all_data2.html', 'w') as file:
    file.write(content)
