import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# Load the preprocessed dataset
df = pd.read_csv('data/preprocessed_gnss_data.csv', delimiter=';')
print(df.head())
# Separate timestamp, lat and long
df = df.drop(columns=['timestamp', 'latitude', 'longitude'])

# Separate features and target variable
X = df.drop('class', axis=1)
y = df['class']
print(X.head())
# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Initialize and train the Random Forest classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred = rf_classifier.predict(X_test)

# Evaluate the model
cm = confusion_matrix(y_test, y_pred)
print('Confusion Matrix:\n', cm)

report = classification_report(y_test, y_pred)
print('Classification Report:\n', report)

feature_importances = pd.Series(rf_classifier.feature_importances_, index=X.columns)
feature_importances.sort_values(ascending=False, inplace=True)
print('Feature Importances:\n', feature_importances)
