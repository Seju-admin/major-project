import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import calendar

# ==========================================
# 1. LOAD AND PREP THE DATA
# ==========================================
print("Loading data... (This might take a minute)")
df = pd.read_excel('forecast.xlsx')
time_col = 'time'

# Convert to datetime and fix the Timezone (UTC to IST +5:30)
df[time_col] = pd.to_datetime(df[time_col], format='%Y%m%d:%H%M')
df[time_col] = df[time_col] + pd.Timedelta(hours=5, minutes=30)
df.set_index(time_col, inplace=True)

# ==========================================
# 2. DATA AGGREGATION
# ==========================================
print("Calculating averages and extreme limits...")

# A. MONTHLY DAY-WISE Averages (Heatmap)
df['Month'] = df.index.month
df['DayOfMonth'] = df.index.day
heatmap_df = df.groupby(['Month', 'DayOfMonth'])['P'].mean().reset_index()
pivot_data = heatmap_df.pivot(index='Month', columns='DayOfMonth', values='P')
month_names = [calendar.month_abbr[i] for i in pivot_data.index]

# B. MONTHLY Averages (For the original Bar graph & Weather)
monthly_avg = df.groupby(df.index.month)[['P', 'Gb(i)', 'Gd(i)', 'T2m']].mean()
monthly_avg['Month_Name'] = [calendar.month_abbr[i] for i in monthly_avg.index]

# C. MONTHLY POWER STATS (Best Day, Worst Day, Average Day) -> For the new Line graph
daily_power = df.groupby(df.index.date)['P'].mean()
daily_power.index = pd.to_datetime(daily_power.index)
monthly_stats = daily_power.groupby(daily_power.index.month).agg(['min', 'max', 'mean'])
monthly_stats['Month_Name'] = [calendar.month_abbr[i] for i in monthly_stats.index]

# D. HOURLY Averages
hourly_avg = df.groupby(df.index.hour)[['P']].mean()

# ==========================================
# 3. BUILD THE DASHBOARD (Now with 6 Plots)
# ==========================================
print("Generating interactive dashboard...")

fig = make_subplots(
    rows=4, cols=2,
    specs=[[{"colspan": 2}, None], # Row 1: Heatmap (Full width)
           [{}, {}],               # Row 2: Monthly Avg Bar | Monthly Limits Line
           [{}, {}],               # Row 3: Hourly Profile | Irradiance
           [{"colspan": 2}, None]],# Row 4: Temperature (Full width)
    subplot_titles=(
        "1. Monthly Day-Wise Power Generation (Heatmap)",
        "2. Monthly Average Power",
        "3. Monthly Power Performance (Best, Avg, Worst Day)",
        "4. Average Daily Profile (IST)",
        "5. Monthly Solar Irradiance",
        "6. Monthly Temperature"
    ),
    vertical_spacing=0.08,
    horizontal_spacing=0.08
)

# --- PLOT 1: Heatmap (Row 1) ---
fig.add_trace(
    go.Heatmap(
        z=pivot_data.values, x=pivot_data.columns, y=month_names,
        colorscale='YlOrRd', name='Power (W)', showscale=True, showlegend=False,
        hovertemplate='Day: %{x}<br>Month: %{y}<br>Avg Power: %{z:.0f} W<extra></extra>'
    ),
    row=1, col=1
)

# --- PLOT 2: Monthly Average Power Bar (Row 2, Left) ---
fig.add_trace(
    go.Bar(x=monthly_avg['Month_Name'], y=monthly_avg['P'],
           name='Monthly Avg Power', marker_color='#2ca02c', showlegend=False),
    row=2, col=1
)

# --- PLOT 3: Monthly Power Limits Line (Row 2, Right) ---
fig.add_trace(
    go.Scatter(x=monthly_stats['Month_Name'], y=monthly_stats['max'],
               mode='lines+markers', name='Max Power (Best Day)',
               line=dict(color='#2ca02c', dash='dot', width=2)),
    row=2, col=2
)
fig.add_trace(
    go.Scatter(x=monthly_stats['Month_Name'], y=monthly_stats['mean'],
               mode='lines+markers', name='Avg Power',
               line=dict(color='#1f77b4', width=4)),
    row=2, col=2
)
fig.add_trace(
    go.Scatter(x=monthly_stats['Month_Name'], y=monthly_stats['min'],
               mode='lines+markers', name='Worst Power (Cloudy Day)',
               line=dict(color='#d62728', dash='dot', width=2)),
    row=2, col=2
)

# --- PLOT 4: Hourly Average (Row 3, Left) ---
fig.add_trace(
    go.Scatter(x=hourly_avg.index, y=hourly_avg['P'],
               mode='lines+markers', name='Hourly Power', showlegend=False,
               line=dict(color='#ff7f0e', width=3), fill='tozeroy'),
    row=3, col=1
)

# --- PLOT 5: Monthly Irradiance (Row 3, Right) ---
fig.add_trace(
    go.Bar(x=monthly_avg['Month_Name'], y=monthly_avg['Gb(i)'],
           name='Direct Irradiance', marker_color='#ffb347', showlegend=False),
    row=3, col=2
)
fig.add_trace(
    go.Bar(x=monthly_avg['Month_Name'], y=monthly_avg['Gd(i)'],
           name='Diffuse Irradiance', marker_color='#aec7e8', showlegend=False),
    row=3, col=2
)
fig.update_layout(barmode='stack')

# --- PLOT 6: Monthly Temperature (Row 4, Full Width) ---
fig.add_trace(
    go.Scatter(x=monthly_avg['Month_Name'], y=monthly_avg['T2m'],
               mode='lines+markers', name='Avg Temp (°C)', showlegend=False,
               line=dict(color='#9467bd', width=3)),
    row=4, col=1
)

# ==========================================
# 4. DASHBOARD STYLING AND EXPORT
# ==========================================
fig.update_layout(
    title_text="Comprehensive Solar PV Forecasting Dashboard",
    title_font_size=26,
    height=1600, # Increased height to fit 4 rows nicely
    width=1400,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
    template="plotly_white",
    hovermode="x unified"
)

# Formatting all axes
fig.update_yaxes(title_text="Month", row=1, col=1)
fig.update_xaxes(title_text="Day of the Month (1-31)", dtick=1, row=1, col=1)

fig.update_yaxes(title_text="Power (W)", row=2, col=1)
fig.update_yaxes(title_text="Power (W)", row=2, col=2)

fig.update_xaxes(title_text="Hour of Day (IST)", tickmode='linear', tick0=0, dtick=2, row=3, col=1)
fig.update_yaxes(title_text="Power (W)", row=3, col=1)
fig.update_yaxes(title_text="Irradiance (W/m²)", row=3, col=2)

fig.update_yaxes(title_text="Temperature (°C)", row=4, col=1)

output_file = "PV_Comprehensive_Dashboard.html"
fig.write_html(output_file)
print(f"Dashboard generated! Open '{output_file}'.")