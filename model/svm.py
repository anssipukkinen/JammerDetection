import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix

# Load the preprocessed dataset
df = pd.read_csv('data/preprocessed_gnss_data.csv', delimiter=';')

# Split the dataset into features (X) and target (y)
X = df.drop('class', axis=1)  # Features
y = df['class']  # Target

# Convert the target variable to binary (if not already in 0/1 format)
y = y.map({'legitimate': 0, 'jammed': 1})  # Encode 'legitimate' as 0 and 'jammed' as 1

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Initialize the SVM classifier
svm_classifier = SVC(kernel='rbf', C=1, gamma='scale', random_state=42)

# Train the classifier
svm_classifier.fit(X_train, y_train)

# Predict on the test set
y_pred = svm_classifier.predict(X_test)

# Evaluate the classifier
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
