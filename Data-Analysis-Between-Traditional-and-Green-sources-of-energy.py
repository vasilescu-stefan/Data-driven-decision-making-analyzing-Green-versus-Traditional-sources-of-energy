import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


BASE_PATH = r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy'


def generate_costs_graphs():
    country_activity_df = pd.read_csv(f'{BASE_PATH}\\excel_conversions\\1_1.csv', skiprows=3)
    country_activity_df['TOTAL'] = pd.to_numeric(country_activity_df['TOTAL'], errors='coerce')
    country_activity_df = country_activity_df.dropna(subset=['Country', 'TOTAL'])

    nuclear_new_temp = pd.read_csv(f'{BASE_PATH}\\excel_conversions\\3_13_a_b1_b2.csv', skiprows=4)
    nuclear_new = nuclear_new_temp.iloc[:, [1, 13]].copy()
    nuclear_new.columns = ['Country', 'LCOE']
    nuclear_new['Category'] = 'Nuclear'

    nuclear = nuclear_new
    try:
        nuclear_lto_temp = pd.read_csv(f'{BASE_PATH}\\excel_conversions\\3_22_a_b1_b2.csv', skiprows=4)
        if not nuclear_lto_temp.empty and nuclear_lto_temp.shape[1] > 13:
            nuclear_lto = nuclear_lto_temp.iloc[:, [1, 13]].copy()
            nuclear_lto.columns = ['Country', 'LCOE']
            nuclear_lto['Category'] = 'Nuclear'
            nuclear = pd.concat([nuclear_new, nuclear_lto])
        else:
            print("Warning (Costs): nuclear_lto file (3_22_a_b1_b2.csv) is empty or has too few columns. Using only new build nuclear data.")
    except FileNotFoundError:
        print("Warning (Costs): nuclear_lto file (3_22_a_b1_b2.csv) not found. Using only new build nuclear data.")
    except IndexError:
        print(f"Warning (Costs): Indexing error while processing nuclear_lto file (3_22_a_b1_b2.csv). Using only new build nuclear data.")


    solar_temp = pd.read_csv(f'{BASE_PATH}\\excel_conversions\\3_14.csv', skiprows=4)
    solar = solar_temp.iloc[:, [1, 14]].copy()
    solar.columns = ['Country', 'LCOE']
    solar['Category'] = 'Green'

    wind_temp = pd.read_csv(f'{BASE_PATH}\\excel_conversions\\3_15_a_b.csv', skiprows=4)
    wind = wind_temp.iloc[:, [1, 13]].copy()
    wind.columns = ['Country', 'LCOE']
    wind['Category'] = 'Green'

    hydro_temp = pd.read_csv(f'{BASE_PATH}\\excel_conversions\\3_16_a_b_c.csv', skiprows=4)
    hydro = hydro_temp.iloc[:, [1, 13]].copy()
    hydro.columns = ['Country', 'LCOE']
    hydro['Category'] = 'Green'

    green = pd.concat([solar, wind, hydro])

    coal_temp = pd.read_csv(f'{BASE_PATH}\\excel_conversions\\3_21.csv', skiprows=4)
    coal = coal_temp.iloc[:, [1, 14]].copy()
    coal.columns = ['Country', 'LCOE']
    coal['Category'] = 'Traditional'

    gas_temp = pd.read_csv(f'{BASE_PATH}\\excel_conversions\\3_20a_b.csv', skiprows=4)
    gas = gas_temp.iloc[:, [1, 14]].copy()
    gas.columns = ['Country', 'LCOE']
    gas['Category'] = 'Traditional'

    traditional = pd.concat([coal, gas])

    combined_data = pd.concat([nuclear, green, traditional])
    combined_data['LCOE'] = pd.to_numeric(combined_data['LCOE'], errors='coerce')
    combined_data['Country'] = combined_data['Country'].str.strip()
    combined_data = combined_data.dropna(subset=['Country', 'LCOE'])

    world_avg = combined_data.groupby('Category')['LCOE'].mean().reset_index()
    print("\nGlobal Average LCOE by Category (Costs.py):")
    print(world_avg)

    if not world_avg.empty:
        fig1 = px.bar(
            world_avg,
            x='Category',
            y='LCOE',
            title='Global Average LCOE by Energy Type ',
            labels={'LCOE': 'LCOE (USD/MWh)', 'Category': 'Energy Type'},
            color='Category',
            color_discrete_map={'Nuclear': 'blue', 'Green': 'green', 'Traditional': 'gray'}
        )
        fig1.update_layout(yaxis_range=[0, world_avg['LCOE'].max() + 20 if not world_avg.empty else 100])
        fig1.show()
    else:
        print("Warning (Costs): world_avg DataFrame is empty. Skipping fig1.")


    country_category_counts = combined_data.groupby('Country')['Category'].nunique()
    countries_with_all_three_types = country_category_counts[country_category_counts == 3].index.tolist()
    print(f"\nCountries with LCOE data for all 3 energy types (Costs.py): {countries_with_all_three_types}")

    top_countries_for_fig2 = []
    if countries_with_all_three_types:
        country_activity_df['Country'] = country_activity_df['Country'].str.strip()
        relevant_country_activity = country_activity_df[country_activity_df['Country'].isin(countries_with_all_three_types)]
        top_countries_for_fig2 = relevant_country_activity.sort_values('TOTAL', ascending=False).head(5)['Country'].tolist()
    
    print(f"Top 5 countries (from those with all 3 types) by activity for Fig 2 (Costs.py): {top_countries_for_fig2}")

    if top_countries_for_fig2:
        top_data_fig2 = combined_data[combined_data['Country'].isin(top_countries_for_fig2)]
        top_avg_fig2 = top_data_fig2.groupby(['Country', 'Category'])['LCOE'].mean().reset_index()
        print("\nAverage LCOE for selected Top Countries (Fig 2 from Costs.py):")
        print(top_avg_fig2)

        if not top_avg_fig2.empty:
            fig2 = px.bar(
                top_avg_fig2,
                x='Country',
                y='LCOE',
                color='Category',
                title='LCOE Comparison for Top Countries with All Energy Types ',
                labels={'LCOE': 'LCOE (USD/MWh)'},
                color_discrete_map={'Nuclear': 'blue', 'Green': 'green', 'Traditional': 'gray'},
                barmode='group',
                category_orders={"Country": top_countries_for_fig2}
            )
            max_lcoe_top_fig2 = top_avg_fig2['LCOE'].max() if not top_avg_fig2.empty else 120
            fig2.update_layout(yaxis_range=[0, max_lcoe_top_fig2 + 20 if pd.notna(max_lcoe_top_fig2) else 120])
            fig2.show()
        else:
            print("Warning (Costs): top_avg_fig2 DataFrame is empty. Skipping fig2.")

    elif countries_with_all_three_types:
        print(f"Found {len(countries_with_all_three_types)} countries with all three types: {countries_with_all_three_types}. Showing data for these.")
        top_data_fig2 = combined_data[combined_data['Country'].isin(countries_with_all_three_types)]
        top_avg_fig2 = top_data_fig2.groupby(['Country', 'Category'])['LCOE'].mean().reset_index()
        print("\nAverage LCOE for countries with all three types (Costs.py):")
        print(top_avg_fig2)
        if not top_avg_fig2.empty:
            fig2 = px.bar(
                top_avg_fig2,
                x='Country',
                y='LCOE',
                color='Category',
                title=f'LCOE Comparison for Countries with All Energy Types ({len(countries_with_all_three_types)} found) ',
                labels={'LCOE': 'LCOE (USD/MWh)'},
                color_discrete_map={'Nuclear': 'blue', 'Green': 'green', 'Traditional': 'gray'},
                barmode='group',
                category_orders={"Country": countries_with_all_three_types}
            )
            max_lcoe_top_fig2 = top_avg_fig2['LCOE'].max() if not top_avg_fig2.empty else 120
            fig2.update_layout(yaxis_range=[0, max_lcoe_top_fig2 + 20 if pd.notna(max_lcoe_top_fig2) else 120])
            fig2.show()
        else:
            print("Warning (Costs): top_avg_fig2 for fewer than 5 countries is empty. Skipping fig2.")
    else:
        print("\nCould not find countries with LCOE data for all three energy types to generate the second plot (Costs.py).")
    print("-" * 50)


def generate_eu_energy_graphs():

    try:
        df_eu = pd.read_csv(f'{BASE_PATH}\\EU_energy data\\EU_energy_data.csv')
    except FileNotFoundError:
        print(f"Error (EUEnergy): EU_energy_data.csv not found at {BASE_PATH}\\EU_energy data\\EU_energy_data.csv. Skipping EU Energy graphs.")
        return

    column_translation = {
        'fecha': 'date', 'hora': 'time', 'sistema': 'system_code',
        'bandera': 'is_green_energy', 'precio': 'price_eur_mwh',
        'tipo_moneda': 'currency_type', 'origen_dato': 'data_source',
        'fecha_actualizacion': 'last_updated'
    }
    df_eu = df_eu.rename(columns=column_translation)

    df_eu['is_green_energy'] = (
        df_eu['is_green_energy']
        .astype(str).str.strip().str.upper()
        .map({'Y': True, '1': True, 'N': False, '0': False})
    )

    if df_eu['is_green_energy'].isna().any():
        print(f"Warning (EUEnergy): {df_eu['is_green_energy'].isna().sum()} unmapped 'is_green_energy' values found. Filling with False.")
        df_eu['is_green_energy'] = df_eu['is_green_energy'].fillna(False)
    
    df_eu['date'] = pd.to_datetime(df_eu['date'], dayfirst=True, errors='coerce')
    df_eu['last_updated'] = pd.to_datetime(df_eu['last_updated'], errors='coerce')
    df_eu['hour'] = pd.to_datetime(df_eu['time'], format='%H:%M:%S', errors='coerce').dt.hour 
    df_eu.dropna(subset=['date', 'hour', 'price_eur_mwh', 'is_green_energy'], inplace=True)

    if df_eu.empty:
        print("Warning (EUEnergy): DataFrame is empty after initial processing. Skipping graphs.")
        return

    price_diff = df_eu.pivot_table(index=['date', 'hour'], 
                                 columns='is_green_energy', 
                                 values='price_eur_mwh',
                                 aggfunc='mean')
    
    if True in price_diff.columns and False in price_diff.columns:
        price_diff['price_diff'] = price_diff[True] - price_diff[False]
        if not price_diff.empty and 'price_diff' in price_diff.columns and not price_diff['price_diff'].isna().all():
            fig_density = px.density_heatmap(price_diff.reset_index(), 
                                    x='hour', y='date', z='price_diff',
                                    nbinsx=24,
                                    title='<b>Green vs Conventional Price Gap (€/MWh)</b><br>Positive = Green more expensive',
                                    color_continuous_scale='RdBu',
                                    range_color=[-50, 50])
            fig_density.update_layout(yaxis_title='Date', xaxis_title='Hour of Day')
            fig_density.show()
        else:
            print("Warning (EUEnergy): price_diff DataFrame for density heatmap is empty or 'price_diff' column is all NaN. Skipping density heatmap.")
    else:
        print("Warning (EUEnergy): Could not create price_diff due to missing True/False columns in pivot. Skipping density heatmap.")


    df_eu['hour_str'] = df_eu['hour'].astype(int).astype(str) + ':00'
    fig_violin = go.Figure()
    for is_green, color in [(True, '#2ecc71'), (False, '#e74c3c')]:
        subset = df_eu[df_eu['is_green_energy'] == is_green]
        if not subset.empty:
            fig_violin.add_trace(go.Violin(
                x=subset['hour_str'], y=subset['price_eur_mwh'],
                name='Green' if is_green else 'Conventional',
                box_visible=True, meanline_visible=True, line_color=color,
                fillcolor=f'rgba({int(color[1:3],16)}, {int(color[3:5],16)}, {int(color[5:],16)}, 0.2)'
            ))
    if fig_violin.data:
        fig_violin.update_layout(
            title='<b>Price Distribution by Hour and Energy Type </b>',
            xaxis_title='Hour of Day', yaxis_title='Price (€/MWh)',
            violingap=0.2, violingroupgap=0
        )
        fig_violin.show()
    else:
        print("Warning (EUEnergy): No data for violin plot. Skipping.")


    hourly_prices = (
        df_eu.set_index('date')
        .groupby(['is_green_energy', pd.Grouper(freq='H')])['price_eur_mwh']
        .agg(['first', 'max', 'min', 'last'])
        .reset_index(level=0)
    )
    if not hourly_prices.empty:
        fig_candlestick = make_subplots(rows=2, cols=1, shared_xaxes=True)
        traces_added = 0
        for i, (is_green, color) in enumerate([(True, 'green'), (False, 'red')], 1):
            subset = hourly_prices[hourly_prices['is_green_energy'] == is_green]
            if not subset.empty:
                fig_candlestick.add_trace(go.Candlestick(
                    x=subset.index, open=subset['first'], high=subset['max'],
                    low=subset['min'], close=subset['last'],
                    name='Green' if is_green else 'Conventional',
                    increasing_line_color=color, decreasing_line_color='gray',
                    showlegend=True
                ), row=i, col=1)
                traces_added +=1
        if traces_added > 0:
            fig_candlestick.update_layout(
                title='<b>Hourly Electricity Price Candlesticks </b><br>Green vs Conventional Energy',
                yaxis_title='Price (€/MWh)', xaxis_title='Date',
                xaxis_rangeslider_visible=False, height=800, hovermode='x unified'
            )
            fig_candlestick.update_xaxes(rangeslider_thickness=0.05, row=2, col=1)
            fig_candlestick.show()
        else:
            print("Warning (EUEnergy): No data for candlestick plot. Skipping.")

    else:
        print("Warning (EUEnergy): hourly_prices DataFrame is empty. Skipping candlestick plot.")


    hourly_avg = df_eu.groupby(['hour', 'is_green_energy'])['price_eur_mwh'].mean().unstack()
    if not hourly_avg.empty and True in hourly_avg.columns and False in hourly_avg.columns:
        fig_mirror = go.Figure()
        fig_mirror.add_trace(go.Bar(
            x=hourly_avg.index, y=hourly_avg[True], name='Green',
            marker_color='#2ecc71', opacity=0.7
        ))
        fig_mirror.add_trace(go.Bar(
            x=hourly_avg.index, y=-hourly_avg[False], name='Conventional',
            marker_color='#e74c3c', opacity=0.7
        ))
        fig_mirror.add_trace(go.Scatter(
            x=hourly_avg.index, y=hourly_avg[True] - hourly_avg[False],
            name='Spread', line=dict(color='purple', width=3)
        ))
        fig_mirror.update_layout(
            title='<b>Mirrored Hourly Prices </b><br>Green (Above) vs Conventional (Below)',
            barmode='relative', yaxis_title="Price (€/MWh)", hovermode='x unified'
        )
        fig_mirror.show()
    else:
        print("Warning (EUEnergy): hourly_avg DataFrame for mirrored plot is empty or missing True/False columns. Skipping.")
    print("-" * 50)


def generate_global_sustainable_energy_graphs():

    try:
        df = pd.read_csv(f'{BASE_PATH}\\Global Data on Sustainable Energy (2000-2020)\\global-data-on-sustainable-energy (1).csv')
    except FileNotFoundError:
        print(f"Error (GlobalSustainable): CSV not found at {BASE_PATH}\\Global Data on Sustainable Energy (2000-2020)\\global-data-on-sustainable-energy (1).csv. Skipping these graphs.")
        return

    print(df.head())
    viz_df = df.copy()
    viz_df['Value_co2_emissions_kt_by_country'] = viz_df['Value_co2_emissions_kt_by_country'].replace(0, 1)
    viz_df = viz_df.dropna(subset=[
        'gdp_per_capita', 'Renewables (% equivalent primary energy)',
        'Value_co2_emissions_kt_by_country'
    ])
    if not viz_df.empty:
        fig_scatter_gdp = px.scatter(viz_df, 
                        x='gdp_per_capita', 
                        y='Renewables (% equivalent primary energy)',
                        size='Value_co2_emissions_kt_by_country',
                        color='Entity', hover_name='Entity', log_x=True,
                        size_max=60,
                        title='Renewable Energy vs GDP (Size = CO2 Emissions)')
        fig_scatter_gdp.show()
    else:
        print("Warning (GlobalSustainable): viz_df for scatter GDP plot is empty. Skipping.")


    latest_year = df['Year'].max()
    year_df = df[df['Year'] == latest_year].copy()
    year_df['Total Electricity (TWh)'] = (year_df['Electricity from fossil fuels (TWh)'].fillna(0) + 
                                         year_df['Electricity from nuclear (TWh)'].fillna(0) + 
                                         year_df['Electricity from renewables (TWh)'].fillna(0))
    year_df = year_df[year_df['Total Electricity (TWh)'] > 0]
    year_df['Low-carbon electricity (% electricity)'] = year_df['Low-carbon electricity (% electricity)'].fillna(0)

    if not year_df.empty:
        fig_treemap = px.treemap(year_df,
                        path=['Entity'], values='Total Electricity (TWh)',
                        color='Low-carbon electricity (% electricity)',
                        color_continuous_scale=['red', 'yellow', 'green'],
                        color_continuous_midpoint=50,
                        hover_data={
                            'Fossil Fuels (TWh)': year_df['Electricity from fossil fuels (TWh)'].round(1),
                            'Renewables (TWh)': year_df['Electricity from renewables (TWh)'].round(1),
                            'Nuclear (TWh)': year_df['Electricity from nuclear (TWh)'].round(1),
                            'Total': year_df['Total Electricity (TWh)'].round(1)
                        },
                        title=f'Global Energy Mix {latest_year} <br><sup>Size=Total Energy, Color=% Low-Carbon</sup>')
        fig_treemap.update_layout(
            margin=dict(t=80, l=0, r=0, b=0),
            coloraxis_colorbar=dict(title='% Low-Carbon', ticksuffix='%')
        )
        fig_treemap.show()
    else:
        print("Warning (GlobalSustainable): year_df for treemap is empty. Skipping.")


    def create_comparison_bars(country, main_df):
        country_data = main_df[(main_df['Entity'] == country) & (main_df['Year'].isin([2000, 2020]))]
        if not country_data.empty:
            fig = px.bar(country_data,
                        x='Year',
                        y=['Electricity from fossil fuels (TWh)',
                           'Electricity from nuclear (TWh)',
                           'Electricity from renewables (TWh)'],
                        barmode='group',
                        title=f'{country} Energy Source Transition ',
                        labels={'value':'Electricity Generation (TWh)'},
                        color_discrete_map={
                            'Electricity from fossil fuels (TWh)':'#E4572E',
                            'Electricity from nuclear (TWh)':'#17BEBB',
                            'Electricity from renewables (TWh)':'#76B041'
                        })
            fig.update_layout(yaxis_title="Electricity Generation (TWh)", legend_title="Energy Source")
            fig.show()
        else:
            print(f"Warning (GlobalSustainable): No data for {country} comparison bars. Skipping.")

    create_comparison_bars('France', df)

    def create_stacked_area(country, main_df):
        country_data = main_df[(main_df['Entity'] == country) & 
                             (main_df['Year'].between(2000, 2020))]
        if not country_data.empty:
            fig = px.area(country_data,
                        x='Year',
                        y=['Electricity from fossil fuels (TWh)',
                           'Electricity from nuclear (TWh)',
                           'Electricity from renewables (TWh)'],
                        title=f'{country} Energy Transition (2000-2020) ',
                        labels={'value':'Electricity Generation (TWh)'},
                        color_discrete_map={
                            'Electricity from fossil fuels (TWh)':'#E4572E',
                            'Electricity from nuclear (TWh)':'#17BEBB',
                            'Electricity from renewables (TWh)':'#76B041'
                        })
            fig.update_layout(yaxis_title="Electricity Generation (TWh)", legend_title="Energy Source")
            fig.show()
        else:
            print(f"Warning (GlobalSustainable): No data for {country} stacked area. Skipping.")
            
    create_stacked_area('France', df)

    def create_animated_barchart(countries, main_df):
        temp_df = main_df[main_df['Entity'].isin(countries)].copy()
        if not temp_df.empty:
            temp_df['Total'] = temp_df[['Electricity from fossil fuels (TWh)',
                                      'Electricity from nuclear (TWh)',
                                      'Electricity from renewables (TWh)']].sum(axis=1)
            if not temp_df.empty and temp_df['Total'].max() > 0 :                                 
                fig = px.bar(temp_df,
                            x='Entity',
                            y=['Electricity from fossil fuels (TWh)',
                                'Electricity from nuclear (TWh)',
                                'Electricity from renewables (TWh)'],
                            animation_frame='Year',
                            range_y=[0, temp_df['Total'].max()*1.1 if not temp_df.empty else 100],
                            title='Energy Source Transition by Country ',
                            color_discrete_map={
                                'Electricity from fossil fuels (TWh)':'#E4572E',
                                'Electricity from nuclear (TWh)':'#17BEBB',
                                'Electricity from renewables (TWh)':'#76B041'
                            })
                fig.update_layout(yaxis_title="Electricity Generation (TWh)", xaxis_title="Country", legend_title="Energy Source")
                fig.show()
            else:
                print("Warning (GlobalSustainable): temp_df for animated barchart has no positive total or is empty. Skipping.")
        else:
            print("Warning (GlobalSustainable): temp_df for animated barchart is empty. Skipping.")


    create_animated_barchart(['Germany', 'France', 'United States', 'China'], df)

    global_df = df.groupby('Year')[['Electricity from fossil fuels (TWh)',
                                  'Electricity from nuclear (TWh)',
                                  'Electricity from renewables (TWh)']].sum().reset_index()
    global_df['Total'] = global_df[['Electricity from fossil fuels (TWh)', 
                                   'Electricity from nuclear (TWh)', 
                                   'Electricity from renewables (TWh)']].sum(axis=1)
    
    global_df = global_df[global_df['Total'] > 0]

    if not global_df.empty:
        global_df['Fossil %'] = (global_df['Electricity from fossil fuels (TWh)'] / global_df['Total']) * 100
        global_df['Nuclear %'] = (global_df['Electricity from nuclear (TWh)'] / global_df['Total']) * 100
        global_df['Renewables %'] = (global_df['Electricity from renewables (TWh)'] / global_df['Total']) * 100

        fig_global_mix = px.bar(global_df, 
                    x='Year', y=['Fossil %', 'Nuclear %', 'Renewables %'],
                    title='<b>Global Electricity Generation Mix </b><br><i>Percentage Breakdown by Source</i>',
                    labels={'value': 'Percentage (%)', 'variable': 'Energy Source'},
                    color_discrete_map={
                        'Fossil %': '#E4572E', 'Nuclear %': '#17BEBB', 'Renewables %': '#76B041'
                    }, text_auto='.1f')
        fig_global_mix.update_layout(
            yaxis_title="Percentage of Total Generation", legend_title="Energy Source",
            hovermode="x unified", barmode='stack'
        )
        fig_global_mix.show()

        melted_global_df = global_df.melt(id_vars='Year', 
                                        value_vars=['Electricity from fossil fuels (TWh)',
                                                    'Electricity from nuclear (TWh)',
                                                    'Electricity from renewables (TWh)'])
        if not melted_global_df.empty:
            fig_global_line = px.line(melted_global_df, 
                        x='Year', y='value', facet_col='variable', facet_col_spacing=0.08,
                        title='<b>Global Electricity Generation by Source Type </b>',
                        labels={'value': 'Generation (TWh)'},
                        color_discrete_sequence=['#E4572E', '#17BEBB', '#76B041'])
            fig_global_line.update_layout(showlegend=False, yaxis_title="Generation (TWh)")
            fig_global_line.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig_global_line.show()
        else:
            print("Warning (GlobalSustainable): melted_global_df for line plot is empty. Skipping.")
    else:
        print("Warning (GlobalSustainable): global_df for mix and line plots is empty after filtering zero totals. Skipping.")


    df_filtered_anim_scatter = df.dropna(subset=[
        'Renewable energy share in the total final energy consumption (%)',
        'Value_co2_emissions_kt_by_country',
        'Primary energy consumption per capita (kWh/person)',
        'Year', 'Entity'
    ])
    if not df_filtered_anim_scatter.empty:
        fig_anim_scatter = px.scatter(
            df_filtered_anim_scatter,
            x='Renewable energy share in the total final energy consumption (%)',
            y='Value_co2_emissions_kt_by_country',
            size='Primary energy consumption per capita (kWh/person)',
            color='Entity', animation_frame='Year', hover_name='Entity',
            log_y=True, range_x=[0, 100],
            title='<b>Renewable Energy Adoption vs CO₂ Emissions Over Time </b>'
        )
        fig_anim_scatter.update_layout(showlegend=False)
        fig_anim_scatter.show()
    else:
        print("Warning (GlobalSustainable): df_filtered_anim_scatter for animated scatter is empty. Skipping.")
    print("-" * 50)


def generate_death_rate_graphs():
    try:
        df_death = pd.read_csv(f'{BASE_PATH}\\Nuclear Energy Datasets\\rates_death_from_energy_production_per_twh.csv')
    except FileNotFoundError:
        print(f"Error (DeathRate): CSV not found at {BASE_PATH}\\Nuclear Energy Datasets\\rates_death_from_energy_production_per_twh.csv. Skipping this graph.")
        return

    df_death['Deaths per TWh of electricity production'] = pd.to_numeric(
        df_death['Deaths per TWh of electricity production'].astype(str).str.replace(',', '.'), 
        errors='coerce'
    )
    df_death = df_death.dropna(subset=['Deaths per TWh of electricity production'])
    
    if not df_death.empty:
        df_death = df_death.sort_values('Deaths per TWh of electricity production', ascending=True)
        fig_death = px.bar(
            df_death,
            x='Deaths per TWh of electricity production', y='Entity',
            orientation='h', color='Deaths per TWh of electricity production',
            color_continuous_scale='RdYlGn_r',
            title='Energy Production Mortality Rates 2021 ',
            labels={'Deaths per TWh of electricity production': 'Deaths/TWh'},
            height=600
        )
        fig_death.update_xaxes(type='log', range=[-1, 2], title='Deaths per TWh (log scale)') 
        fig_death.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            coloraxis_colorbar=dict(title='Deaths/TWh'),
            template='plotly_white'
        )
        fig_death.show()
    else:
        print("Warning (DeathRate): df_death is empty after processing. Skipping graph.")
    print("-" * 50)


def generate_global_energy_substitution_graphs():
    try:
        df_sub = pd.read_csv(f'{BASE_PATH}\\Global Energy Substitution from 1983 to 2022\\global-energy-substitution.csv')
    except FileNotFoundError:
        print(f"Error (EnergySub): CSV not found at {BASE_PATH}\\Global Energy Substitution from 1983 to 2022\\global-energy-substitution.csv. Skipping these graphs.")
        return

    df_sub.set_index('Year', inplace=True)

    total_energy = df_sub.sum().sort_values(ascending=False)
    if not total_energy.empty:
        fig1_sub = px.bar(total_energy, 
                        title='Total Energy Consumption by Source (1983-2022) ',
                        labels={'value': 'Energy Units', 'index': 'Energy Source'},
                        color=total_energy.index)
        fig1_sub.update_layout(xaxis_tickangle=-45)
        fig1_sub.show()
    else:
        print("Warning (EnergySub): total_energy Series is empty. Skipping fig1_sub.")


    fossil_fuels = df_sub[['Coal', 'Oil', 'Gas']].sum(axis=1)
    renewables = df_sub[['Hydropower', 'Wind', 'Solar', 'Biofuels', 'Other_renewables']].sum(axis=1)
    fig2_sub = go.Figure()
    fig2_sub.add_trace(go.Scatter(x=df_sub.index, y=fossil_fuels, mode='lines', name='Fossil Fuels (Coal+Oil+Gas)'))
    fig2_sub.add_trace(go.Scatter(x=df_sub.index, y=renewables, mode='lines', name='Renewables (Hydro+Wind+Solar+Bio)'))
    fig2_sub.add_trace(go.Scatter(x=df_sub.index, y=df_sub['Nuclear'], mode='lines', name='Nuclear'))
    fig2_sub.update_layout(title='Fossil Fuels vs Renewables vs Nuclear Over Time ', yaxis_title='Energy Units')
    fig2_sub.show()

    renewable_sources = ['Solar', 'Wind', 'Biofuels', 'Other_renewables', 'Hydropower']
    fig3_sub = px.line(df_sub[renewable_sources], 
                    title='Growth of Renewable Energy Sources ',
                    labels={'value': 'Energy Units', 'Year': 'Year'})
    fig3_sub.update_layout(hovermode='x unified')
    fig3_sub.show()

    energy_mix_cols = ['Coal', 'Oil', 'Gas', 'Nuclear', 'Hydropower', 'Wind', 'Solar', 'Biofuels']
    valid_energy_mix_cols = [col for col in energy_mix_cols if col in df_sub.columns]

    if valid_energy_mix_cols:
        fig_mix_sub = px.area(
            df_sub[valid_energy_mix_cols],
            title="🌍 Global Energy Mix Over Time ",
            labels={'value': 'Energy Units', 'Year': 'Year'}
        )
        fig_mix_sub.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig_mix_sub.show()
    else:
        print("Warning (EnergySub): No valid columns for energy mix area chart. Skipping.")


    if 1983 in df_sub.index and 2022 in df_sub.index:
        year_1983 = df_sub.loc[1983].drop('Traditional_biomass', errors='ignore')
        year_2022 = df_sub.loc[2022].drop('Traditional_biomass', errors='ignore')
        
        if not year_1983.empty and not year_2022.empty:
            fig_comparison_sub = make_subplots(rows=1, cols=2, specs=[[{'type': 'pie'}, {'type': 'pie'}]], subplot_titles=['1983 Energy Mix', '2022 Energy Mix'])
            fig_comparison_sub.add_trace(
                go.Pie(labels=year_1983.index, values=year_1983.values, name='1983', hole=0.3, marker_colors=px.colors.qualitative.Pastel),
                row=1, col=1
            )
            fig_comparison_sub.add_trace(
                go.Pie(labels=year_2022.index, values=year_2022.values, name='2022', hole=0.3, marker_colors=px.colors.qualitative.Pastel),
                row=1, col=2
            )
            fig_comparison_sub.update_layout(
                title_text='⚡ Energy Mix Comparison: 1983 vs. 2022 ', showlegend=True,
                annotations=[dict(text='1983', x=0.18, y=1.1, font_size=15, showarrow=False),
                             dict(text='2022', x=0.82, y=1.1, font_size=15, showarrow=False)]
            )
            fig_comparison_sub.update_traces(textposition='inside', textinfo='percent+label')
            fig_comparison_sub.show()
        else:
            print("Warning (EnergySub): Data for 1983 or 2022 is empty after dropping Traditional_biomass. Skipping pie comparison.")
    else:
        print("Warning (EnergySub): Year 1983 or 2022 not found in index. Skipping pie comparison.")


    energy_mix_anim_cols = ['Coal', 'Oil', 'Gas', 'Nuclear', 'Hydropower', 'Wind', 'Solar', 'Biofuels', 'Other_renewables']
    valid_energy_mix_anim_cols = [col for col in energy_mix_anim_cols if col in df_sub.columns]
    years = df_sub.index.unique()

    if valid_energy_mix_anim_cols and not df_sub.loc[df_sub.index.min()][valid_energy_mix_anim_cols].empty:
        fig_anim_pie_sub = go.Figure()
        fig_anim_pie_sub.add_trace(
            go.Pie(
                labels=valid_energy_mix_anim_cols,
                values=df_sub.loc[df_sub.index.min()][valid_energy_mix_anim_cols],
                name=str(df_sub.index.min()), hole=0.3, marker_colors=px.colors.qualitative.Pastel
            )
        )
        frames = []
        for year_val in years:
            frames.append(
                go.Frame(
                    data=[go.Pie(
                        labels=valid_energy_mix_anim_cols,
                        values=df_sub.loc[year_val][valid_energy_mix_anim_cols],
                        name=str(year_val))
                    ],
                    name=str(year_val)
                )
            )
        fig_anim_pie_sub.frames = frames
        fig_anim_pie_sub.update_layout(
            title="🌍 Evolution of Global Energy Mix (1983-2022) ",
            updatemenus=[{
                "type": "buttons",
                "buttons": [
                    {"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 1000}, "fromcurrent": True}]},
                    {"label": "Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}]}
                ], "x": 0.1, "y": 0
            }],
            sliders=[{
                "steps": [{"args": [[f.name], {"frame": {"duration": 0}, "mode": "immediate"}],
                            "label": f.name, "method": "animate"} for f in frames],
                "x": 0.1, "len": 0.9, "currentvalue": {"prefix": "Year: "}
            }]
        )
        fig_anim_pie_sub.update_traces(textposition='inside', textinfo='percent+label')
        fig_anim_pie_sub.show()
    else:
        print("Warning (EnergySub): No valid columns or initial data for animated pie chart. Skipping.")

    print("-" * 50)

if __name__ == "__main__":
    
    generate_costs_graphs()
    generate_eu_energy_graphs()
    generate_global_sustainable_energy_graphs()
    generate_death_rate_graphs()
    generate_global_energy_substitution_graphs()
    
