import pandas as pd
import numpy as np
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    max_error,
    explained_variance_score
)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

print("🚀 Starting the Machine Learning Training Phase (CNN-LSTM)...")

# 1. LOAD AND PREP THE DATA
print("Loading dataset...")
df = pd.read_excel('forecast.xlsx')
df['time'] = pd.to_datetime(df['time'], format='%Y%m%d:%H%M')

# 2. FEATURE ENGINEERING
print("Extracting features for the AI...")
df['Hour'] = df['time'].dt.hour
df['Month'] = df['time'].dt.month

features = ['Gb(i)', 'Gd(i)', 'T2m', 'Hour', 'Month']
target = 'P'

# 3. SCALE THE FEATURES (Crucial for Deep Learning)
print("Scaling features...")
scaler_X = MinMaxScaler()
df[features] = scaler_X.fit_transform(df[features])

# Save the scaler so logic.py can use it for the Open-Meteo live data
joblib.dump(scaler_X, 'scaler_X.pkl')
print("✅ Feature Scaler saved as 'scaler_X.pkl'")

# 4. CREATE 3D SEQUENCES (Sliding Window Approach)
SEQ_LENGTH = 4  # Model looks at the past 4 hours to predict the next hour


def create_sequences(features_data, target_data, seq_length):
    X, y = [], []
    for i in range(len(features_data) - seq_length):
        X.append(features_data[i:(i + seq_length)])
        y.append(target_data[i + seq_length])
    return np.array(X), np.array(y)


print(f"Creating 3D Sequences (Window Size = {SEQ_LENGTH} hours)...")
X_seq, y_seq = create_sequences(df[features].values, df[target].values, SEQ_LENGTH)

# 5. TRAIN/TEST SPLIT
# For time-series, shuffle=False is better to keep the time order intact
X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.2, random_state=42, shuffle=False)

# 6. BUILDING THE CNN-LSTM MODEL
print("🧠 Building the CNN-LSTM Architecture...")
model = Sequential([
    # CNN block: Extracts spatial/local patterns across the 5 features
    Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(SEQ_LENGTH, len(features))),
    MaxPooling1D(pool_size=2),

    # LSTM block: Remembers the sequence over time
    LSTM(50, activation='relu', return_sequences=False),

    # Output block
    Dense(25, activation='relu'),
    Dense(1)  # Predicts the single power value 'P'
])

model.compile(optimizer='adam', loss='mse')

# Stop training early if the model stops improving (prevents overfitting)
early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

print("⏳ Training started... (This might take a few minutes)")
# epochs=20 means it will go through your dataset 20 times max
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=20, batch_size=64, callbacks=[early_stop],
          verbose=1)

# 7. EVALUATING THE MODEL
print("\n📊 Evaluating Model Performance on Test Data...\n")
predictions = model.predict(X_test).flatten()

r2 = r2_score(y_test, predictions)
evs = explained_variance_score(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
mae = mean_absolute_error(y_test, predictions)
max_err = max_error(y_test, predictions)

# Create a mask to ignore nighttime (where actual power is 0)
daytime_mask = y_test > 0.1  # Only consider when actual power is greater than 0.1 Watts

# Calculate MAPE only for daytime data using numpy
if daytime_mask.sum() > 0:
    mape = np.mean(np.abs((y_test[daytime_mask] - predictions[daytime_mask]) / y_test[daytime_mask])) * 100
else:
    mape = 0.0

# --- SAVING METRICS TO JSON ---
metrics_dict = {
    "r2": float(r2),
    "evs": float(evs),
    "rmse": float(rmse),
    "mae": float(mae),
    "mape": float(mape),
    "max_error": float(max_err)
}

with open('model_metrics.json', 'w') as f:
    json.dump(metrics_dict, f)
print("✅ Metrics saved successfully to 'model_metrics.json'")

# 8. SAVING THE MODEL
# Neural Networks are saved as .h5 or .keras, not .pkl
model.save('solar_cnn_lstm.h5')
print("🎉 Success! The CNN-LSTM model is saved and ready for the Streamlit App.")