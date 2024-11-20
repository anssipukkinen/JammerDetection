# Model Evaluation Results

This document presents the evaluation results of different machine learning models tested on the GNSS jammer detection task.

## Random Forest Model

### Configuration 1: All Features Except Timestamp/Coordinates
```python
# Dropped columns: ['timestamp', 'latitude', 'longitude']
```

#### Classification Report
```
               precision    recall  f1-score   support

      jammed       0.96      0.93      0.95       327
  legitimate       0.98      0.99      0.98      1011

    accuracy                           0.97      1338
   macro avg       0.97      0.96      0.96      1338
weighted avg       0.97      0.97      0.97      1338
```

#### Feature Importance
| Feature               | Importance |
|----------------------|------------|
| num_satellites       | 0.478053   |
| height              | 0.220326   |
| AGC                 | 0.192433   |
| SNR                 | 0.094346   |
| constellation_GPS    | 0.007060   |
| constellation_Galileo| 0.005821   |
| constellation_QZSS   | 0.001961   |

### Configuration 2: Only AGC and SNR

#### Classification Report
```
               precision    recall  f1-score   support

      jammed       0.89      0.83      0.86       327
  legitimate       0.94      0.97      0.96      1011

    accuracy                           0.93      1338
   macro avg       0.92      0.90      0.91      1338
weighted avg       0.93      0.93      0.93      1338
```

#### Confusion Matrix
```
[[270  57]
 [ 33 978]]
```

#### Feature Importance
| Feature | Importance |
|---------|------------|
| AGC     | 0.687296   |
| SNR     | 0.312704   |

---

## XGBoost Model

### Configuration 1: All Features

#### Classification Report
```
              precision    recall  f1-score   support

  legitimate       1.00      1.00      1.00      1011
      jammed       1.00      1.00      1.00       327

    accuracy                           1.00      1338
   macro avg       1.00      1.00      1.00      1338
weighted avg       1.00      1.00      1.00      1338
```

#### Confusion Matrix
```
[[1011    0]
 [   1  326]]
```

#### Feature Importance
| Feature               | Importance |
|----------------------|------------|
| num_satellites       | 0.780707   |
| timestamp           | 0.144059   |
| latitude            | 0.037288   |
| longitude           | 0.014349   |
| height              | 0.013855   |
| AGC                 | 0.007887   |
| SNR                 | 0.001855   |
| constellation_GPS    | 0.000000   |
| constellation_Galileo| 0.000000   |
| constellation_QZSS   | 0.000000   |

### Configuration 2: Without num_satellites

#### Classification Report
```
              precision    recall  f1-score   support

  legitimate       1.00      1.00      1.00      1011
      jammed       0.98      1.00      0.99       327

    accuracy                           1.00      1338
   macro avg       0.99      1.00      0.99      1338
weighted avg       1.00      1.00      1.00      1338
```

#### Confusion Matrix
```
[[1006    5]
 [   0  327]]
```

#### Feature Importance
| Feature               | Importance |
|----------------------|------------|
| height               | 0.257316   |
| timestamp           | 0.205795   |
| constellation_Galileo| 0.187076   |
| latitude            | 0.157341   |
| AGC                 | 0.121468   |
| longitude           | 0.041175   |
| SNR                 | 0.022738   |
| constellation_GPS    | 0.007090   |
| constellation_QZSS   | 0.000000   |

### Configuration 3: Without num_satellites and height

#### Classification Report
```
              precision    recall  f1-score   support

  legitimate       1.00      1.00      1.00      1011
      jammed       0.99      0.99      0.99       327

    accuracy                           0.99      1338
   macro avg       0.99      0.99      0.99      1338
weighted avg       0.99      0.99      0.99      1338
```

#### Confusion Matrix
```
[[1008    3]
 [   4  323]]
```

#### Feature Importance
| Feature               | Importance |
|----------------------|------------|
| latitude             | 0.430986   |
| timestamp           | 0.322697   |
| AGC                 | 0.155457   |
| longitude           | 0.059228   |
| SNR                 | 0.031632   |
| constellation_GPS    | 0.000000   |
| constellation_Galileo| 0.000000   |
| constellation_QZSS   | 0.000000   |

### Configuration 4: Only AGC and SNR

```python
# Dropped columns: ['timestamp', 'num_satellites', 'height', 'latitude', 'longitude',
#                  'constellation_GPS', 'constellation_Galileo', 'constellation_QZSS']
```

#### Classification Report
```
              precision    recall  f1-score   support

  legitimate       0.96      0.97      0.96       674
      jammed       0.90      0.87      0.89       218

    accuracy                           0.95       892
   macro avg       0.93      0.92      0.92       892
weighted avg       0.94      0.95      0.94       892
```

#### Confusion Matrix
```
[[654  20]
 [ 29 189]]
```

#### Feature Importance
| Feature | Importance |
|---------|------------|
| AGC     | 0.624583   |
| SNR     | 0.375417   |

---

## Bagging Classifier

### Configuration: Only AGC and SNR

#### Classification Report
```
              precision    recall  f1-score   support

           0       0.95      0.96      0.96      1011
           1       0.87      0.86      0.86       327

    accuracy                           0.93      1338
   macro avg       0.91      0.91      0.91      1338
weighted avg       0.93      0.93      0.93      1338
```

#### Confusion Matrix
```
[[968  43]
 [ 47 280]]
```

#### Feature Importance
| Feature | Importance |
|---------|------------|
| AGC     | 0.228475   |
| SNR     | 0.162332   |

---

## Support Vector Machine (SVM)

SVM implementation was attempted but failed due to NaN values in the dataset. The error message suggests:

1. Consider using sklearn.ensemble.HistGradientBoostingClassifier/Regressor which handles NaN values natively
2. Preprocess the data using an imputer transformer
3. Drop samples with missing values

Error details:
```
ValueError: Input X contains NaN.
SVC does not accept missing values encoded as NaN natively.
