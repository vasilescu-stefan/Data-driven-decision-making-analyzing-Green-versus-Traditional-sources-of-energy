import plotly.express as px
import pandas as pd

# Read data from CSV file
df = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\Nuclear Energy Datasets\rates_death_from_energy_production_per_twh.csv')  # Update with your actual file path/name

df['Deaths per TWh of electricity production'] = pd.to_numeric(
    df['Deaths per TWh of electricity production'].astype(str).str.replace(',', '.'), 
    errors='coerce'
)

# Remove any problematic rows
df = df.dropna(subset=['Deaths per TWh of electricity production'])

# Sort and plot
df = df.sort_values('Deaths per TWh of electricity production', ascending=True)

fig = px.bar(
    df,
    x='Deaths per TWh of electricity production',
    y='Entity',
    orientation='h',
    color='Deaths per TWh of electricity production',
    color_continuous_scale='RdYlGn_r',
    title='Energy Production Mortality Rates 2021',
    labels={'Deaths per TWh of electricity production': 'Deaths/TWh'},
    height=600
)

# Set axis limits
fig.update_xaxes(
    type='log',
    range=[-1, 2],  # 0.1 to 100
    title='Deaths per TWh (log scale)'
)

fig.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    coloraxis_colorbar=dict(title='Deaths/TWh'),
    template='plotly_white'
)

fig.show()