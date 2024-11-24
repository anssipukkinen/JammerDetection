import pandas as pd
from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Load the preprocessed dataset
df = pd.read_csv('data/preprocessed_gnss_data.csv', delimiter=';')
print(df.head())

# Drop columns (leaves only AGC and SNR)
#df = df.drop(columns=['timestamp', 'num_satellites', 'height', 'latitude', 'longitude'])
#df = df.drop(columns=['num_satellites', 'height','latitude', 'longitude'])
df = df.drop(columns=['num_satellites','height','timestamp', 'latitude', 'longitude'])

# Encode the 'class' column to binary values
df['class'] = df['class'].map({'legitimate': 0, 'jammed': 1})

# Separate features (X) and target (y)
X = df.drop(columns=['class'])
y = df['class']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Initialize the base estimator
base_estimator = DecisionTreeClassifier(random_state=42)

# Initialize the BaggingClassifier
bagging_clf = BaggingClassifier(estimator=base_estimator, n_estimators=50, random_state=42)

# Train the classifier
bagging_clf.fit(X_train, y_train)

# Predict on the test set
y_pred = bagging_clf.predict(X_test)

# Evaluate the classifier
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

from sklearn.inspection import permutation_importance

result = permutation_importance(bagging_clf, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1)

# Create a pandas Series for easy visualization
feature_importances = pd.Series(result.importances_mean, index=X_test.columns)

# Sort and display feature importances
feature_importances = feature_importances.sort_values(ascending=False)
print(feature_importances)
