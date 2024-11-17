import folium
from folium.plugins import TimestampedGeoJson
import pandas as pd
import json
import branca.colormap as cm

# Sample data
data = {
    'timestamp': [1725970911064.0, 1725970911064.0, 1725970911065.0],
    'constellation': ['GLONASS', 'GPS', 'Galileo'],
    'AGC': [59.924476623535156, 28.13314437866211, 28.13314437866211],
    'SNR': [66.0, 70.0, 58.0],
    'latitude': [69.212375, 69.212375, 69.212375],
    'longitude': [15.858584, 15.858584, 15.858584],
    'height': [11.8, 11.8, 11.8]
}

# Create DataFrame
df = pd.read_csv('output.csv')

# Normalize AGC for color mapping
#agc_min = df['AGC'].min()
#agc_max = df['AGC'].max()
#df['AGC_normalized'] = (df['AGC'] - agc_min) / (agc_max - agc_min)

# Normalize SNR for marker size scaling
snr_min = df['SNR'].min()
snr_max = df['SNR'].max()
df['SNR_normalized'] = (df['SNR'] - snr_min) / (snr_max - snr_min)

# Convert timestamp to ISO format
df['time'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%dT%H:%M:%SZ')

# Create a colormap for AGC values
#colormap = cm.LinearColormap(colors=['blue', 'red'], vmin=agc_min, vmax=agc_max, caption='AGC Value')
colormap = cm.LinearColormap(colors=['blue', 'red'], vmin=df['AGC'].min(), vmax=df['AGC'].max(), caption='AGC Value')

# Create GeoJSON features
features = []
for _, row in df.iterrows():
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [row['longitude'], row['latitude']],
        },
        'properties': {
            'time': row['time'],
            'popup': f"Constellation: {row['constellation']}<br>AGC: {row['AGC']}<br>SNR: {row['SNR']}",
            'icon': 'circle',
            'iconstyle': {
                'fillColor': colormap(row['AGC']),
                'fillOpacity': 0.6,
                'stroke': 'true',
                'radius': 5 + row['SNR_normalized'] * 10  # Base radius plus scaled SNR
            }
        }
    }
    features.append(feature)

# Create GeoJSON
geojson = {
    'type': 'FeatureCollection',
    'features': features
}

# Initialize map
m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=10)

# Add TimestampedGeoJson with speed control
TimestampedGeoJson(
    data=json.dumps(geojson),
    transition_time=200,  # milliseconds
    loop=False,
    auto_play=True,
    add_last_point=True,
    period='PT1S',  # ISO 8601 duration format
    speed_slider=True,  # Enable speed control slider
    min_speed=0.1,  # Minimum speed (0.1x)
    max_speed=10,   # Maximum speed (10x)
    loop_button=True,  # Enable loop button
    time_slider_drag_update=True  # Update map when dragging time slider
).add_to(m)

# Add colormap to map
colormap.add_to(m)

# Save map to HTML
m.save('animated_map_with_agc_snr.html')
