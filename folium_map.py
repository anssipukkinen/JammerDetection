import folium
from folium.plugins import TimestampedGeoJson
import pandas as pd
import json
import branca.colormap as cm

# Create DataFrame
df = pd.read_csv('output.csv')

# Normalize SNR for marker size scaling
snr_min = df['SNR'].min()
snr_max = df['SNR'].max()
df['SNR_normalized'] = (df['SNR'] - snr_min) / (snr_max - snr_min)

# Convert timestamp to ISO format
df['time'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%dT%H:%M:%SZ')

# Create a colormap for AGC values
colormap = cm.LinearColormap(colors=['blue', 'red'], vmin=df['AGC'].min(), vmax=df['AGC'].max(), caption='AGC Value')

# Create GeoJSON features
features = []
for idx, row in df.iterrows():
    # Create tooltip content
    tooltip_content = (
        f"Time: {row['time']}<br>"
        f"Constellation: {row['constellation']}<br>"
        f"AGC: {row['AGC']:.2f}<br>"
        f"SNR: {row['SNR']:.2f}<br>"
        f"Lat: {row['latitude']:.6f}<br>"
        f"Lon: {row['longitude']:.6f}<br>"
        f"Height: {row['height']:.2f}"
    )
    
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
                'fillColor': colormap(row['AGC']),
                'fillOpacity': 0.6,
                'stroke': 'true',
                'radius': 5 + row['SNR_normalized'] * 10
            },
            'style': {'color': colormap(row['AGC'])},
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

# Initialize map
m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=10)

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
m.save('animated_map_with_agc_snr_with_tooltips.html')

# Add custom CSS to the saved file to style tooltips
with open('animated_map_with_agc_snr_with_tooltips.html', 'r') as file:
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

with open('animated_map_with_agc_snr_with_tooltips2.html', 'w') as file:
    file.write(content)
