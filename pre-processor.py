import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Load the dataset
df = pd.read_csv('data.csv', delimiter=';')

# Remove records for the BeiDou constellation
df = df[df['constellation'] != 'BeiDou']

# Handle missing values in 'AGC'
df['AGC'].fillna(df['AGC'].median(), inplace=True)

# One-Hot Encode the 'constellation' feature
encoder = OneHotEncoder(sparse_output=False, drop='first')
encoded_constellation = encoder.fit_transform(df[['constellation']])
encoded_df = pd.DataFrame(encoded_constellation, columns=encoder.get_feature_names_out(['constellation']))
df = pd.concat([df.reset_index(drop=True), encoded_df], axis=1)
df.drop('constellation', axis=1, inplace=True)

# Normalize 'AGC', 'SNR', 'latitude', and 'longitude' features
scaler = StandardScaler()
columns_to_normalize = ['AGC', 'SNR', 'latitude', 'longitude']
df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])

# Save the preprocessed data (optional)
df.to_csv('preprocessed_gnss_data.csv', index=False, sep=';')
