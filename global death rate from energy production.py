import plotly.express as px
import pandas as pd

df = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\Nuclear Energy Datasets\rates_death_from_energy_production_per_twh.csv')

df['Deaths per TWh of electricity production'] = pd.to_numeric(
    df['Deaths per TWh of electricity production'].astype(str).str.replace(',', '.'), 
    errors='coerce'
)

df = df.dropna(subset=['Deaths per TWh of electricity production'])

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


fig.update_xaxes(
    type='log',
    range=[-1, 2],
    title='Deaths per TWh (log scale)'
)

fig.update_layout(
    yaxis={'categoryorder': 'total ascending'},
    coloraxis_colorbar=dict(title='Deaths/TWh'),
    template='plotly_white'
)

fig.show()