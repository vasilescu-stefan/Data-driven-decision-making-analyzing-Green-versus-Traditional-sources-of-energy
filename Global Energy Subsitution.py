import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the data
df = pd.read_csv('Data-Analysis-Between-Traditional-and-Green-sources-of-energy\Global Energy Substitution from 1983 to 2022\global-energy-substitution.csv')

# Set Year as index for better plotting
df.set_index('Year', inplace=True)

# 1. Total Energy Consumption by Source
total_energy = df.sum().sort_values(ascending=False)
fig1 = px.bar(total_energy, 
              title='Total Energy Consumption by Source (1983-2022)',
              labels={'value': 'Energy Units', 'index': 'Energy Source'},
              color=total_energy.index)
fig1.update_layout(xaxis_tickangle=-45)

# 2. Fossil Fuels vs Renewables Over Time
fossil_fuels = df[['Coal', 'Oil', 'Gas']].sum(axis=1)
renewables = df[['Hydropower', 'Wind', 'Solar', 'Biofuels', 'Other_renewables']].sum(axis=1)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df.index, y=fossil_fuels, 
                         mode='lines', name='Fossil Fuels (Coal+Oil+Gas)'))
fig2.add_trace(go.Scatter(x=df.index, y=renewables, 
                         mode='lines', name='Renewables (Hydro+Wind+Solar+Bio)'))
fig2.add_trace(go.Scatter(x=df.index, y=df['Nuclear'], 
                         mode='lines', name='Nuclear'))
fig2.update_layout(title='Fossil Fuels vs Renewables vs Nuclear Over Time',
                  yaxis_title='Energy Units')

# 3. Growth of Renewable Energy Sources
renewable_sources = ['Solar', 'Wind', 'Biofuels', 'Other_renewables', 'Hydropower']
fig3 = px.line(df[renewable_sources], 
              title='Growth of Renewable Energy Sources',
              labels={'value': 'Energy Units', 'Year': 'Year'})
fig3.update_layout(hovermode='x unified')

# Show all figures
fig1.show()
fig2.show()
fig3.show()



energy_mix = ['Coal', 'Oil', 'Gas', 'Nuclear', 'Hydropower', 'Wind', 'Solar', 'Biofuels']
fig_mix = px.area(
    df[energy_mix],
    title="🌍 Global Energy Mix Over Time",
    labels={'value': 'Energy Units', 'Year': 'Year'}
)
fig_mix.update_layout(
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
fig_mix.show()


from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Data for 1983 and 2022
year_1983 = df.loc[1983].drop('Traditional_biomass')
year_2022 = df.loc[2022].drop('Traditional_biomass')

# Create subplots
fig_comparison = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'pie'}]], subplot_titles=['1983 Energy Mix', '2022 Energy Mix'])

# Add 1983 pie
fig_comparison.add_trace(
    go.Pie(
        labels=year_1983.index,
        values=year_1983.values,
        name='1983',
        hole=0.3,
        marker_colors=px.colors.qualitative.Pastel
    ),
    row=1, col=1
)

# Add 2022 pie
fig_comparison.add_trace(
    go.Pie(
        labels=year_2022.index,
        values=year_2022.values,
        name='2022',
        hole=0.3,
        marker_colors=px.colors.qualitative.Pastel
    ),
    row=1, col=2
)

# Update layout
fig_comparison.update_layout(
    title_text='⚡ Energy Mix Comparison: 1983 vs. 2022',
    showlegend=True,
    annotations=[dict(text='1983', x=0.18, y=1.1, font_size=15, showarrow=False),
                 dict(text='2022', x=0.82, y=1.1, font_size=15, showarrow=False)]
)
fig_comparison.update_traces(textposition='inside', textinfo='percent+label')

fig_comparison.show()


####
import plotly.graph_objects as go

# Prepare data (drop 'Traditional_biomass' for clarity)
energy_mix = ['Coal', 'Oil', 'Gas', 'Nuclear', 'Hydropower', 'Wind', 'Solar', 'Biofuels', 'Other_renewables']
years = df.index.unique()

# Create initial figure
fig = go.Figure()

# Add initial pie trace (1983)
fig.add_trace(
    go.Pie(
        labels=energy_mix,
        values=df.loc[1983][energy_mix],
        name="1983",
        hole=0.3,
        marker_colors=px.colors.qualitative.Pastel
    )
)

# Add animation frames
frames = []
for year in years:
    frames.append(
        go.Frame(
            data=[go.Pie(
                labels=energy_mix,
                values=df.loc[year][energy_mix],
                name=str(year))
            ],
            name=str(year)
        )
    )

# Add all frames to the figure
fig.frames = frames

# Add play/pause button and slider
fig.update_layout(
    title="🌍 Evolution of Global Energy Mix (1983-2022)",
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {
                "label": "Play",
                "method": "animate",
                "args": [None, {"frame": {"duration": 1000}, "fromcurrent": True}]
            },
            {
                "label": "Pause",
                "method": "animate",
                "args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}]
            }
        ],
        "x": 0.1,
        "y": 0
    }],
    sliders=[{
        "steps": [{
            "args": [[f.name], {"frame": {"duration": 0}, "mode": "immediate"}],
            "label": f.name,
            "method": "animate"
        } for f in frames],
        "x": 0.1,
        "len": 0.9,
        "currentvalue": {"prefix": "Year: "}
    }]
)

# Update traces for % labels
fig.update_traces(textposition='inside', textinfo='percent+label')

fig.show()