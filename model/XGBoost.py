import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load the preprocessed dataset
df = pd.read_csv('data/preprocessed_gnss_data.csv', delimiter=';')
print(df.head())

# Drop columns (leaves only AGC and SNR)
#df = df.drop(columns=['num_satellites'])
df = df.drop(columns=['num_satellites', 'height'])
#df = df.drop(columns=['timestamp', 'num_satellites', 'height', 'latitude', 'longitude'])
df = df.drop(columns=['timestamp', 'latitude', 'longitude'])
#df = df.drop(columns=['num_satellites', 'height','latitude', 'longitude'])
#df = df.drop(columns=['timestamp','num_satellites', 'height', 'latitude', 'longitude'])
#df = df.drop(columns=['timestamp', 'num_satellites', 'latitude', 'longitude'])


# Encode the 'class' column to binary values
df['class'] = df['class'].map({'legitimate': 0, 'jammed': 1})

# Separate features (X) and target (y)
X = df.drop(columns=['class'])
y = df['class']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix

# Initialize the XGBoost classifier
xgb_classifier = xgb.XGBClassifier(
    objective='binary:logistic',
    eval_metric='logloss',
    random_state=42
)

# Train the classifier
xgb_classifier.fit(X_train, y_train)

# Predict on the test set
y_pred = xgb_classifier.predict(X_test)

# Classification report
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=['legitimate', 'jammed']))

# Confusion matrix
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

import matplotlib.pyplot as plt
import xgboost as xgb

# Plot feature importance
#xgb.plot_importance(xgb_classifier)
#plt.show()
feature_importances = pd.Series(xgb_classifier.feature_importances_, index=X.columns)
feature_importances.sort_values(ascending=False, inplace=True)
print('Feature Importances:\n', feature_importances)
