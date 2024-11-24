import pandas as pd
from sklearn.preprocessing import StandardScaler

# Load the dataset
df = pd.read_csv('data/manual_data_with_classes.csv', delimiter=';')

# Drop rows with empty location coordinates 2-74
df = df.drop(df.index[1:74])  # Index 1-73 corresponds to rows 2-74

# Remove records for the BeiDou constellation
df = df[df['constellation'] != 'BeiDou']

# Handle missing values in 'AGC'
df['AGC'].fillna(df['AGC'].median(), inplace=True)

# Drop the constellation column
df.drop('constellation', axis=1, inplace=True)

# Normalize 'AGC', 'SNR', 'latitude', and 'longitude' features
scaler = StandardScaler()
columns_to_normalize = ['AGC', 'SNR', 'latitude', 'longitude', 'height', 'num_satellites']
df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])

# Save the preprocessed data (optional)
df.to_csv('data/preprocessed_gnss_data.csv', index=False, sep=';')
