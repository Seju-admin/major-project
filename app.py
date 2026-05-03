import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Import our custom backend logic
import solar_logic

# ==========================================
# 1. PAGE SETUP & THEME (Academic/Professional UI)
# ==========================================
st.set_page_config(
    page_title="HelioCast-AI | PV Forecaster",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injecting Custom CSS for a Professional, Formal Look
st.markdown("""
<style>
    /* Apply Times New Roman/Professional Serif Font globally */
    html, body, [class*="css"] {
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* Headers Styling */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Times New Roman', Times, serif !important;
        color: #00E5FF !important; /* Kept the technical cyan accent */
    }

    /* Style the tabs to look more formal */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E1E1E;
        border: 1px solid #00E5FF;
        border-radius: 4px;
        padding: 10px 20px;
        font-family: 'Times New Roman', Times, serif !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00E5FF;
        color: #000000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR (Credits & Project Info)
# ==========================================
with st.sidebar:
    st.markdown("## HelioCast-AI")
    st.markdown("*Advanced PV Climatology & Generation Forecasting Engine*")
    st.markdown("---")
    st.markdown("### Primary Investigators:")
    st.info("**Shobhit Sharma**\n\nRoll No: 12214131")
    st.info("**Karun Thakur**\n\nRoll No: 12214132")
    st.markdown("---")
    st.markdown("**Institution:**\n\nNational Institute of Technology (NIT), Kurukshetra")
    # ENGINE UPDATED HERE
    st.markdown("**Engine:** Spatio-Temporal CNN-LSTM Neural Network")
    st.markdown("**Data Feed:** Open-Meteo Live API")


# ==========================================
# 3. MAIN DASHBOARD HEADER
# ==========================================
@st.cache_resource
def load_model_cached():
    return solar_logic.load_ml_model()

# NAYA: Ab yeh 'model' nahi, 'model_objects' tuple hai (model + scaler)
model_objects = load_model_cached()

st.title("HelioCast-AI: PV Forecasting Terminal")
st.markdown("Real-time telemetry and deep-learning based predictive modeling for Solar Photovoltaic arrays.")

# NAYA: Tuple ke first element (model) ko check kar rahe hain
if model_objects[0] is None:
    st.error("CRITICAL ERROR: AI model ('solar_cnn_lstm.h5') or Scaler ('scaler_X.pkl') not found in the directory.")
    st.stop()

# ==========================================
# 4. DASHBOARD TABS
# ==========================================
tab1, tab2 = st.tabs(["Live API Telemetry", "Manual Simulation Matrix"])

# ------------------------------------------
# TAB 1: LIVE API FORECAST
# ------------------------------------------
with tab1:
    st.markdown("### Geographic Target Selection")

    locations = {
        "NIT Kurukshetra (Campus)": {"lat": 29.9495, "lon": 76.8161},
        "Kurukshetra City Grid": {"lat": 29.9695, "lon": 76.8223},
        "Custom Coordinates": {"lat": 29.9695, "lon": 76.8223}
    }

    col_loc1, col_loc2 = st.columns([1, 2])

    with col_loc1:
        selected_location = st.selectbox("Select Target Node", list(locations.keys()))
        if selected_location == "Custom Coordinates":
            lat = st.number_input("Latitude", value=locations["Custom Coordinates"]["lat"], format="%.4f")
            lon = st.number_input("Longitude", value=locations["Custom Coordinates"]["lon"], format="%.4f")
        else:
            lat = locations[selected_location]["lat"]
            lon = locations[selected_location]["lon"]
            st.success(f"**Target Locked:** {selected_location}\n\n**Lat:** {lat}° N | **Lon:** {lon}° E")

    with col_loc2:
        st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=13, use_container_width=True)

    if st.button("Initiate Live Data Fetch & Prediction", type="primary"):
        with st.spinner(f'Establishing connection with Open-Meteo Satellite Database for {selected_location}...'):
            try:
                # Backend Logic Call (Passing the tuple)
                api_df = solar_logic.get_live_forecast(lat, lon, model_objects)

                st.toast('Connection Successful! Processing Neural Network Outputs...')

                st.markdown("---")
                st.markdown("### Predicted 7-Day Average Yield Matrix")

                daily_avg = api_df.groupby(api_df['time'].dt.date)['Predicted_Power (W)'].mean().reset_index()
                daily_avg.columns = ['Date', 'Avg_Power']

                meter_cols = st.columns(len(daily_avg))

                for idx, row in daily_avg.iterrows():
                    with meter_cols[idx]:
                        # Scientific Dark Mode Gauge
                        fig_gauge = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=row['Avg_Power'],
                            title={'text': row['Date'].strftime('%a, %b %d'),
                                   'font': {'size': 14, 'color': 'white', 'family': 'Times New Roman'}},
                            number={'suffix': " W",
                                    'font': {'size': 18, 'color': '#00E5FF', 'family': 'Times New Roman'}},
                            gauge={
                                'axis': {'range': [None, 1500], 'tickwidth': 1, 'tickcolor': "white"},
                                'bar': {'color': "#00E5FF"},  # Cyan Bar
                                'bgcolor': "#1E1E1E",
                                'borderwidth': 2,
                                'bordercolor': "#444",
                                'steps': [
                                    {'range': [0, 500], 'color': "#2b0a0a"},  # Dark Red (Low)
                                    {'range': [500, 1000], 'color': "#332900"},  # Dark Yellow (Mid)
                                    {'range': [1000, 1500], 'color': "#003314"}  # Dark Green (High)
                                ]
                            }
                        ))
                        fig_gauge.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10),
                                                paper_bgcolor="#0e1117",
                                                font={'color': "white", 'family': 'Times New Roman'})
                        st.plotly_chart(fig_gauge, use_container_width=True)

                st.markdown("### High-Resolution Generation Trajectory")
                # Dark Mode Area Chart
                fig = px.area(api_df, x='time', y='Predicted_Power (W)',
                              labels={'time': 'Timestamp (IST)', 'Predicted_Power (W)': 'Power Output (Watts)'},
                              color_discrete_sequence=['#00E5FF'], template="plotly_dark")

                # Apply Times New Roman to the Plotly Graph
                fig.update_layout(
                    hovermode="x unified",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Times New Roman, Times, serif", color="white")
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("Access Raw Telemetry Data"):
                    st.dataframe(api_df, use_container_width=True)

            except Exception as e:
                st.error(f"SYSTEM FAILURE: {e}")

# ------------------------------------------
# TAB 2: MANUAL SIMULATOR
# ------------------------------------------
with tab2:
    st.markdown("### Manual Parameter Overrides")
    col1, col2 = st.columns([1, 2])

    with col1:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        selected_month = st.selectbox("Temporal Input (Month)", months)
        month = months.index(selected_month) + 1

        hour = st.slider("Temporal Input (Hour of Day)", 0, 23, 12)
        gb_i = st.slider("Direct Irradiance Flux [W/m²]", 0.0, 1200.0, 800.0)
        gd_i = st.slider("Diffuse Irradiance Flux [W/m²]", 0.0, 600.0, 150.0)
        t2m = st.slider("Ambient Temperature [°C]", 0.0, 50.0, 30.0)

        # Backend Call (Passing the tuple)
        pred_power = solar_logic.get_manual_prediction(gb_i, gd_i, t2m, hour, month, model_objects)

    with col2:
        # Dark Mode Manual Gauge
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred_power,
            title={'text': "Instantaneous Output (W)", 'font': {'color': 'white', 'family': 'Times New Roman'}},
            number={'suffix': " W", 'font': {'color': '#00E5FF', 'family': 'Times New Roman'}},
            gauge={'axis': {'range': [None, 3500], 'tickcolor': "white"},
                   'bar': {'color': "#00E5FF"},
                   'bgcolor': "#1E1E1E"}
        ))
        fig2.update_layout(paper_bgcolor="#0e1117", font={'color': "white", 'family': 'Times New Roman'})
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# 5. MODEL METRICS & EXPLANATION WINDOW
# ==========================================
st.markdown("---")
with st.expander("DIAGNOSTICS: AI Model Performance & Mathematical Formulations"):
    # Fetch live metrics from logic file
    metrics = solar_logic.load_metrics()

    if metrics:
        st.markdown("### Live Model Health (From Last Training Session)")

        # Creating a nice 3-column layout for the metrics
        m_col1, m_col2, m_col3 = st.columns(3)

        with m_col1:
            st.metric(label="R² Score (Accuracy)", value=f"{metrics['r2']:.4f}", delta="Target: 1.0", delta_color="off")
            st.metric(label="Mean Abs. Error (MAE)", value=f"{metrics['mae']:.2f} W")

        with m_col2:
            st.metric(label="RMSE (Standard Deviation)", value=f"{metrics['rmse']:.2f} W")
            st.metric(label="Expl. Variance Score", value=f"{metrics['evs']:.4f}")

        with m_col3:
            st.metric(label="MAPE (Percentage Error)", value=f"{metrics['mape']:.2f} %", delta="Lower is better",
                      delta_color="inverse")
            st.metric(label="Max Error (Worst Case)", value=f"{metrics['max_error']:.2f} W")

        st.markdown("---")

        # NAYA: Feature Importance ki jagah Deep Learning explanation
        st.markdown("### AI Decision Logic: Deep Learning Architecture")
        st.info("Unlike traditional Machine Learning models (which evaluate inputs in isolation), this **Spatio-Temporal CNN-LSTM Network** extracts complex patterns over time. The Convolutional (CNN) layers identify spatial correlations between real-time irradiance and temperature, while the Long Short-Term Memory (LSTM) layers maintain a 4-hour temporal memory to understand weather trajectories, cloud cover momentum, and sunset curves.")
        st.markdown("---")

    # Notice the 'r' right before the triple quotes below!
    # This renders the mathematical formulas correctly.
    st.markdown(r"""
    ### Telemetry Metrics Explained
    Since the objective is to predict a continuous power output (measured in Watts), the engine utilizes **Regression Metrics** to quantify prediction accuracy. Below are the mathematical formulations and operational definitions for each metric used to evaluate the model. 

    *(Note: Let $y_i$ be the actual value, $\hat{y}_i$ be the predicted value, $\bar{y}$ be the mean of actual values, and $n$ be the number of samples).*

    #### 1. Coefficient of Determination (R² Score)
    $$R^2 = 1 - \frac{\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}{\sum_{i=1}^{n}(y_i - \bar{y})^2}$$

    * **Definition:** Represents the proportion of the variance in the dependent variable (Power) that is predictable from the independent variables (Weather conditions).
    * **Application:** Evaluates the overall goodness-of-fit. A score of 1.0 indicates a perfect mathematical fit, meaning the model accounts for all variance in the data.

    #### 2. Root Mean Square Error (RMSE)
    $$RMSE = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}$$

    * **Definition:** The standard deviation of the prediction errors (residuals). 
    * **Application:** Because the errors are squared before being averaged, RMSE heavily penalizes larger errors. This is highly useful in power grid forecasting to identify severe prediction anomalies (e.g., unexpected power drops).

    #### 3. Mean Absolute Error (MAE)
    $$MAE = \frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|$$

    * **Definition:** The arithmetic average of the absolute errors between predicted and actual values.
    * **Application:** Provides a linear, straightforward interpretation of the average error margin in Watts. Unlike RMSE, it treats all errors equally regardless of their magnitude.

    #### 4. Mean Absolute Percentage Error (MAPE)
    $$MAPE = \frac{100\%}{n}\sum_{i=1}^{n}\left|\frac{y_i - \hat{y}_i}{y_i}\right|$$

    * **Definition:** Evaluates the average percentage difference between the predicted and actual power values.
    * **Application:** Offers an intuitive relative error metric (e.g., "The model is off by 5% on average"). In this system, it is calculated exclusively for daylight hours to prevent division-by-zero errors when actual power generation is 0 W.

    #### 5. Explained Variance Score (EVS)
    $$EVS = 1 - \frac{Var(y - \hat{y})}{Var(y)}$$

    * **Definition:** Measures the proportion to which a mathematical model accounts for the variation of a given dataset.
    * **Application:** Similar to the R² score, but EVS specifically accounts for the mean error of predictions. If the mean error is exactly zero, EVS equals R².

    #### 6. Maximum Residual Error (Max Error)
    $$Max Error = \max(|y_i - \hat{y}_i|)$$

    * **Definition:** Captures the single largest deviation between a predicted value and its corresponding actual value.
    * **Application:** Acts as a worst-case scenario indicator. It informs grid operators of the maximum possible discrepancy they might face under the model's current testing conditions.
    """)