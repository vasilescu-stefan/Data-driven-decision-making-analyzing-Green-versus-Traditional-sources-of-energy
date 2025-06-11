import pandas as pd
import plotly.express as px

df = pd.read_csv('Data-Analysis-Between-Traditional-and-Green-sources-of-energy\Global Data on Sustainable Energy (2000-2020)\global-data-on-sustainable-energy (1).csv')  # Replace with your actual file path

# Display the first few rows to understand the structure
print(df.head())

viz_df = df.copy()

# Fill/replace zeros in size column (CO2 emissions)
viz_df['Value_co2_emissions_kt_by_country'] = viz_df['Value_co2_emissions_kt_by_country'].replace(0, 1)  # Replace 0 with 1 kt

# Filter out rows with missing values in key columns
viz_df = viz_df.dropna(subset=[
    'gdp_per_capita',
    'Renewables (% equivalent primary energy)',
    'Value_co2_emissions_kt_by_country'
])

# Now create the visualization
fig = px.scatter(viz_df, 
                 x='gdp_per_capita', 
                 y='Renewables (% equivalent primary energy)',
                 size='Value_co2_emissions_kt_by_country',
                 color='Entity',
                 hover_name='Entity', 
                 log_x=True,
                 size_max=60,
                 title='Renewable Energy vs GDP (Size = CO2 Emissions)')
fig.show()

# Filter most recent year
latest_year = df['Year'].max()
year_df = df[df['Year'] == latest_year].copy()

# Calculate total electricity (handle missing values)
year_df['Total Electricity (TWh)'] = (year_df['Electricity from fossil fuels (TWh)'].fillna(0) + 
                                     year_df['Electricity from nuclear (TWh)'].fillna(0) + 
                                     year_df['Electricity from renewables (TWh)'].fillna(0))

# Filter out countries with zero total electricity
year_df = year_df[year_df['Total Electricity (TWh)'] > 0]

# Handle missing/zero values in the color variable
year_df['Low-carbon electricity (% electricity)'] = year_df['Low-carbon electricity (% electricity)'].fillna(0)

# Create visualization with safety checks
if not year_df.empty:
    fig = px.treemap(year_df,
                    path=['Entity'],
                    values='Total Electricity (TWh)',
                    color='Low-carbon electricity (% electricity)',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    color_continuous_midpoint=50,  # 50% as midpoint
                    hover_data={
                        'Fossil Fuels (TWh)': year_df['Electricity from fossil fuels (TWh)'].round(1),
                        'Renewables (TWh)': year_df['Electricity from renewables (TWh)'].round(1),
                        'Nuclear (TWh)': year_df['Electricity from nuclear (TWh)'].round(1),
                        'Total': year_df['Total Electricity (TWh)'].round(1)
                    },
                    title=f'Global Energy Mix {latest_year} <br><sup>Size=Total Energy, Color=% Low-Carbon</sup>')
    
    # Adjust layout for readability
    fig.update_layout(
        margin=dict(t=80, l=0, r=0, b=0),
        coloraxis_colorbar=dict(
            title='% Low-Carbon',
            ticksuffix='%'
        )
    )
    fig.show()
else:
    print("No valid data available for visualization after filtering.")



def create_comparison_bars(country):
    country_data = df[(df['Entity'] == country) & (df['Year'].isin([2000, 2020]))]
    
    fig = px.bar(country_data,
                 x='Year',
                 y=['Electricity from fossil fuels (TWh)',
                    'Electricity from nuclear (TWh)',
                    'Electricity from renewables (TWh)'],
                 barmode='group',
                 title=f'{country} Energy Source Transition',
                 labels={'value':'Electricity Generation (TWh)'},
                 color_discrete_map={
                     'Electricity from fossil fuels (TWh)':'#E4572E',
                     'Electricity from nuclear (TWh)':'#17BEBB',
                     'Electricity from renewables (TWh)':'#76B041'
                 })
    
    fig.update_layout(
        yaxis_title="Electricity Generation (TWh)",
        legend_title="Energy Source"
    )
    return fig

create_comparison_bars('France').show()

def create_stacked_area(country):
    country_data = df[(df['Entity'] == country) & 
                     (df['Year'].between(2000, 2020))]
    
    fig = px.area(country_data,
                  x='Year',
                  y=['Electricity from fossil fuels (TWh)',
                     'Electricity from nuclear (TWh)',
                     'Electricity from renewables (TWh)'],
                  title=f'{country} Energy Transition (2000-2020)',
                  labels={'value':'Electricity Generation (TWh)'},
                  color_discrete_map={
                      'Electricity from fossil fuels (TWh)':'#E4572E',
                      'Electricity from nuclear (TWh)':'#17BEBB',
                      'Electricity from renewables (TWh)':'#76B041'
                  })
    
    fig.update_layout(
        yaxis_title="Electricity Generation (TWh)",
        legend_title="Energy Source"
    )
    return fig

create_stacked_area('France').show()


def create_animated_barchart(countries):
    temp_df = df[df['Entity'].isin(countries)].copy()
    temp_df['Total'] = temp_df[['Electricity from fossil fuels (TWh)',
                              'Electricity from nuclear (TWh)',
                              'Electricity from renewables (TWh)']].sum(axis=1)
    
    fig = px.bar(temp_df,
                 x='Entity',
                 y=['Electricity from fossil fuels (TWh)',
                    'Electricity from nuclear (TWh)',
                    'Electricity from renewables (TWh)'],
                 animation_frame='Year',
                 range_y=[0, temp_df['Total'].max()*1.1],
                 title='Energy Source Transition by Country',
                 color_discrete_map={
                     'Electricity from fossil fuels (TWh)':'#E4572E',
                     'Electricity from nuclear (TWh)':'#17BEBB',
                     'Electricity from renewables (TWh)':'#76B041'
                 })
    
    fig.update_layout(
        yaxis_title="Electricity Generation (TWh)",
        xaxis_title="Country",
        legend_title="Energy Source"
    )
    return fig

create_animated_barchart(['Germany', 'France', 'United States', 'China']).show()

# Aggregate global data
# Calculate percentages
global_df = df.groupby('Year')[['Electricity from fossil fuels (TWh)',
                              'Electricity from nuclear (TWh)',
                              'Electricity from renewables (TWh)']].sum().reset_index()
global_df['Total'] = global_df.sum(axis=1)
global_df['Fossil %'] = (global_df['Electricity from fossil fuels (TWh)'] / global_df['Total']) * 100
global_df['Nuclear %'] = (global_df['Electricity from nuclear (TWh)'] / global_df['Total']) * 100
global_df['Renewables %'] = (global_df['Electricity from renewables (TWh)'] / global_df['Total']) * 100

fig = px.bar(global_df, 
             x='Year',
             y=['Fossil %', 'Nuclear %', 'Renewables %'],
             title='<b>Global Electricity Generation Mix</b><br><i>Percentage Breakdown by Source</i>',
             labels={'value': 'Percentage (%)', 'variable': 'Energy Source'},
             color_discrete_map={
                 'Fossil %': '#E4572E',
                 'Nuclear %': '#17BEBB',
                 'Renewables %': '#76B041'
             },
             text_auto='.1f')

fig.update_layout(
    yaxis_title="Percentage of Total Generation",
    legend_title="Energy Source",
    hovermode="x unified",
    barmode='stack'
)
fig.show()

fig = px.line(global_df.melt(id_vars='Year', 
                            value_vars=['Electricity from fossil fuels (TWh)',
                                       'Electricity from nuclear (TWh)',
                                       'Electricity from renewables (TWh)']), 
              x='Year', 
              y='value',
              facet_col='variable',
              facet_col_spacing=0.08,
              title='<b>Global Electricity Generation by Source Type</b>',
              labels={'value': 'Generation (TWh)'},
              color_discrete_sequence=['#E4572E', '#17BEBB', '#76B041'])

fig.update_layout(
    showlegend=False,
    yaxis_title="Generation (TWh)"
)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
fig.show()

fig = px.scatter(
    df,
    x='Renewable energy share in the total final energy consumption (%)',
    y='Value_co2_emissions_kt_by_country',
    size='Primary energy consumption per capita (kWh/person)',
    color='Entity',
    animation_frame='Year',
    hover_name='Entity',
    log_y=True,
    range_x=[0, 100],
    title='<b>Renewable Energy Adoption vs CO₂ Emissions Over Time</b>'
)
fig.update_layout(showlegend=False)
fig.show()