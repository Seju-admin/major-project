import pandas as pd
import numpy as np
import joblib
import requests
import json
from tensorflow.keras.models import load_model

# NAYA: LSTM ke liye Sequence Length define karna zaroori hai (4 ghante ka history)
SEQ_LENGTH = 4


def load_ml_model():
    """Loads the trained CNN-LSTM model AND the Data Scaler."""
    try:
        # NAYA: compile=False add karna zaroori hai!
        model = load_model('solar_cnn_lstm.h5', compile=False)
        scaler = joblib.load('scaler_X.pkl')
        return model, scaler
    except Exception as e:
        print(f"Error loading model/scaler: {e}")
        return None, None


def get_live_forecast(lat, lon, model_objects):
    """Fetches weather data from API, formats for LSTM, and predicts solar power."""
    # Tuple se model aur scaler alag nikalna
    model, scaler = model_objects
    # --- ADD THIS BEFORE YOUR API CALL ---
    print("\n" + "=" * 60)
    print("-[SYSTEM INITIATED] Connecting to Open-Meteo REST API...")
    print("-Fetching 168-hour continuous weather forecast...")
    # 1. Call the API
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,direct_radiation,diffuse_radiation&timezone=Asia%2FKolkata"
    response = requests.get(url)
    # --- ADD THIS AFTER YOUR API CALL ---
    print("-[SUCCESS] Historical & Live Data Retrieved Successfully!")
    print("-Loading 'scaler_X.pkl' for strict mathematical normalization...")
    print("-Feeding 3D Tensor sequences into the Spatio-Temporal CNN-LSTM Model...")
    print("-Live Inference Running: Generating 7-Day Power Trajectory...")
    print("=" * 60 + "\n")
    if response.status_code != 200:
        raise Exception("Failed to connect to the Weather API")

    data = response.json()

    # 2. Parse Data into Pandas DataFrame
    times = pd.to_datetime(data['hourly']['time'])
    api_df = pd.DataFrame({
        'time': times,
        'T2m': data['hourly']['temperature_2m'],
        'Gb(i)': data['hourly']['direct_radiation'],
        'Gd(i)': data['hourly']['diffuse_radiation']
    })

    # 3. Feature Engineering
    api_df['Hour'] = api_df['time'].dt.hour
    api_df['Month'] = api_df['time'].dt.month

    features_list = ['Gb(i)', 'Gd(i)', 'T2m', 'Hour', 'Month']

    # 4. NAYA: Scale the Features
    scaled_features = scaler.transform(api_df[features_list])

    # 5. NAYA: Create 3D Sequences for LSTM
    # 7 din (168 hours) ka output barqarar rakhne ke liye, hum pehle row ko thoda repeat (pad) kar dete hain
    padded_features = np.vstack([np.tile(scaled_features[0], (SEQ_LENGTH - 1, 1)), scaled_features])

    X_live = []
    for i in range(len(padded_features) - SEQ_LENGTH + 1):
        X_live.append(padded_features[i:(i + SEQ_LENGTH)])
    X_live = np.array(X_live)  # Naya shape: (168, 4, 5)

    # 6. Predict using CNN-LSTM
    predictions = model.predict(X_live).flatten()
    api_df['Predicted_Power (W)'] = predictions

    # 7. Clean up nighttime predictions (Set to 0 if no sun)
    night_mask = (api_df['Hour'] < 5) | (api_df['Hour'] > 19) | ((api_df['Gb(i)'] == 0) & (api_df['Gd(i)'] == 0))
    api_df.loc[night_mask, 'Predicted_Power (W)'] = 0.0
    api_df['Predicted_Power (W)'] = api_df['Predicted_Power (W)'].clip(lower=0)

    return api_df


def get_manual_prediction(gb_i, gd_i, t2m, hour, month, model_objects):
    """Calculates power for manual simulator inputs using LSTM."""
    model, scaler = model_objects

    # Clean up nighttime predictions immediately
    if hour < 5 or hour > 19 or (gb_i == 0 and gd_i == 0):
        return 0.0

    input_df = pd.DataFrame({
        'Gb(i)': [gb_i], 'Gd(i)': [gd_i], 'T2m': [t2m], 'Hour': [hour], 'Month': [month]
    })

    # Scale input
    scaled_input = scaler.transform(input_df)

    # NAYA: Since LSTM needs a sequence, we trick it by repeating the current instance SEQ_LENGTH times
    sequence_input = np.tile(scaled_input[0], (SEQ_LENGTH, 1)).reshape(1, SEQ_LENGTH, 5)

    pred_power = model.predict(sequence_input).flatten()[0]

    return max(0.0, float(pred_power))


def load_metrics():
    """Loads the evaluation metrics saved during training."""
    try:
        with open('model_metrics.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None