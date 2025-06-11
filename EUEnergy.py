import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load data
df_eu = pd.read_csv('Data-Analysis-Between-Traditional-and-Green-sources-of-energy\EU_energy data\EU_energy_data.csv')

# 1. Rename columns
column_translation = {
    'fecha': 'date',
    'hora': 'time',
    'sistema': 'system_code',
    'bandera': 'is_green_energy',
    'precio': 'price_eur_mwh',
    'tipo_moneda': 'currency_type',
    'origen_dato': 'data_source',
    'fecha_actualizacion': 'last_updated'
}
df_eu = df_eu.rename(columns=column_translation)

# 2. Robust boolean conversion
df_eu['is_green_energy'] = (
    df_eu['is_green_energy']
    .astype(str).str.strip().str.upper()
    .map({'Y': True, '1': True, 'N': False, '0': False})
)

# 3. Handle remaining NAs (if any)
if df_eu['is_green_energy'].isna().any():
    print(f"Warning: {df_eu['is_green_energy'].isna().sum()} unmapped values found")
    # Option 1: Fill NAs with False (conservative)
    df_eu['is_green_energy'] = df_eu['is_green_energy'].fillna(False)
    
    # Option 2: Keep as NA and investigate
    # print(df_eu[df_eu['is_green_energy'].isna()]['is_green_energy'].value_counts())

# 4. Convert other types
df_eu['date'] = pd.to_datetime(df_eu['date'], dayfirst=True)
df_eu['last_updated'] = pd.to_datetime(df_eu['last_updated'])

df_eu['hour'] = pd.to_datetime(df_eu['time']).dt.hour

# Calculate price difference between green/conventional
price_diff = df_eu.pivot_table(index=['date', 'hour'], 
                             columns='is_green_energy', 
                             values='price_eur_mwh',
                             aggfunc='mean')
price_diff['price_diff'] = price_diff[True] - price_diff[False]  # Green - Conventional

fig = px.density_heatmap(price_diff.reset_index(), 
                        x='hour', 
                        y='date', 
                        z='price_diff',
                        nbinsx=24,
                        title='<b>Green vs Conventional Price Gap (€/MWh)</b><br>Positive = Green more expensive',
                        color_continuous_scale='RdBu',
                        range_color=[-50, 50])  # Adjust based on your data range
fig.update_layout(yaxis_title='Date', xaxis_title='Hour of Day')
fig.show()

if 'hour' not in df_eu.columns:
    df_eu['hour'] = pd.to_datetime(df_eu['time']).dt.hour

# Create hour labels
df_eu['hour_str'] = df_eu['hour'].astype(str) + ':00'

fig = go.Figure()

for is_green, color in [(True, '#2ecc71'), (False, '#e74c3c')]:
    subset = df_eu[df_eu['is_green_energy'] == is_green]
    fig.add_trace(go.Violin(
        x=subset['hour_str'],
        y=subset['price_eur_mwh'],
        name='Green' if is_green else 'Conventional',
        box_visible=True,
        meanline_visible=True,
        line_color=color,
        fillcolor=f'rgba({int(color[1:3],16)}, {int(color[3:5],16)}, {int(color[5:],16)}, 0.2)'
    ))

fig.update_layout(
    title='<b>Price Distribution by Hour and Energy Type</b>',
    xaxis_title='Hour of Day',
    yaxis_title='Price (€/MWh)',
    violingap=0.2,
    violingroupgap=0
)
fig.show()




hourly_prices = (
    df_eu.set_index('date')
    .groupby(['is_green_energy', pd.Grouper(freq='H')])['price_eur_mwh']
    .agg(['first', 'max', 'min', 'last'])
    .reset_index(level=0)  # Bring is_green_energy back as column
)

# 2. Create figure
fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

# 3. Add traces for each energy type
for i, (is_green, color) in enumerate([(True, 'green'), (False, 'red')], 1):
    subset = hourly_prices[hourly_prices['is_green_energy'] == is_green]
    
    fig.add_trace(go.Candlestick(
        x=subset.index,
        open=subset['first'],
        high=subset['max'],
        low=subset['min'],
        close=subset['last'],
        name='Green' if is_green else 'Conventional',
        increasing_line_color=color,
        decreasing_line_color='gray',
        showlegend=True
    ), row=i, col=1)

# 4. Update layout
fig.update_layout(
    title='<b>Hourly Electricity Price Candlesticks</b><br>Green vs Conventional Energy',
    yaxis_title='Price (€/MWh)',
    xaxis_title='Date',
    xaxis_rangeslider_visible=False,
    height=800,
    hovermode='x unified'
)

# Add range slider
fig.update_xaxes(
    rangeslider_thickness=0.05,
    row=2, col=1
)

fig.show()


hourly_avg = df_eu.groupby(['hour', 'is_green_energy'])['price_eur_mwh'].mean().unstack()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=hourly_avg.index,
    y=hourly_avg[True],
    name='Green',
    marker_color='#2ecc71',
    opacity=0.7
))
fig.add_trace(go.Bar(
    x=hourly_avg.index,
    y=-hourly_avg[False],  # Mirror below axis
    name='Conventional',
    marker_color='#e74c3c',
    opacity=0.7
))

# Add spread line
fig.add_trace(go.Scatter(
    x=hourly_avg.index,
    y=hourly_avg[True] - hourly_avg[False],
    name='Spread',
    line=dict(color='purple', width=3)
))

fig.update_layout(
    title='<b>Mirrored Hourly Prices</b><br>Green (Above) vs Conventional (Below)',
    barmode='relative',
    yaxis_title="Price (€/MWh)",
    hovermode='x unified'
)
fig.show()