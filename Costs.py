

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


country_activity_df = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\1_1.csv', skiprows=3)

country_activity_df['TOTAL'] = pd.to_numeric(country_activity_df['TOTAL'], errors='coerce')
country_activity_df = country_activity_df.dropna(subset=['Country', 'TOTAL'])

nuclear_new_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_13_a_b1_b2.csv', skiprows=4)
nuclear_new = nuclear_new_temp.iloc[:, [1, 13]].copy()
nuclear_new.columns = ['Country', 'LCOE']
nuclear_new['Category'] = 'Nuclear'


try:
    nuclear_lto_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_22_a_b1_b2.csv', skiprows=4)
    nuclear_lto = nuclear_lto_temp.iloc[:, [1, 13]].copy()
    nuclear_lto.columns = ['Country', 'LCOE']
    nuclear_lto['Category'] = 'Nuclear'
    nuclear = pd.concat([nuclear_new, nuclear_lto])
except FileNotFoundError:
    print("Warning: nuclear_lto file (3_22_a_b1_b2.csv) not found. Using only new build nuclear data.")
    nuclear = nuclear_new
except IndexError:
    print(f"Warning: Indexing error while processing nuclear_lto file (3_22_a_b1_b2.csv) - check column indices {1, 13}. Using only new build nuclear data.")
    nuclear = nuclear_new



solar_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_14.csv', skiprows=4)
solar = solar_temp.iloc[:, [1, 14]].copy() 
solar.columns = ['Country', 'LCOE']
solar['Category'] = 'Green'


wind_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_15_a_b.csv', skiprows=4)
wind = wind_temp.iloc[:, [1, 13]].copy()
wind.columns = ['Country', 'LCOE']
wind['Category'] = 'Green'


hydro_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_16_a_b_c.csv', skiprows=4)
hydro = hydro_temp.iloc[:, [1, 13]].copy() 
hydro.columns = ['Country', 'LCOE']
hydro['Category'] = 'Green'

green = pd.concat([solar, wind, hydro])

coal_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_21.csv', skiprows=4)
coal = coal_temp.iloc[:, [1, 14]].copy()
coal.columns = ['Country', 'LCOE']
coal['Category'] = 'Traditional'

gas_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_20a_b.csv', skiprows=4)
gas = gas_temp.iloc[:, [1, 14]].copy()
gas.columns = ['Country', 'LCOE']
gas['Category'] = 'Traditional'

traditional = pd.concat([coal, gas])


combined_data = pd.concat([nuclear, green, traditional])
combined_data['LCOE'] = pd.to_numeric(combined_data['LCOE'], errors='coerce')
combined_data['Country'] = combined_data['Country'].str.strip()
combined_data = combined_data.dropna(subset=['Country', 'LCOE'])


world_avg = combined_data.groupby('Category')['LCOE'].mean().reset_index()
print("\nGlobal Average LCOE by Category:")
print(world_avg)


fig1 = px.bar(
    world_avg,
    x='Category',
    y='LCOE',
    title='Global Average LCOE by Energy Type',
    labels={'LCOE': 'LCOE (USD/MWh)', 'Category': 'Energy Type'},
    color='Category',
    color_discrete_map={'Nuclear': 'blue', 'Green': 'green', 'Traditional': 'gray'}
)
fig1.update_layout(yaxis_range=[0, world_avg['LCOE'].max() + 20 if not world_avg.empty else 100])
fig1.show()



country_category_counts = combined_data.groupby('Country')['Category'].nunique()
countries_with_all_three_types = country_category_counts[country_category_counts == 3].index.tolist()

print(f"\nCountries with LCOE data for all 3 energy types: {countries_with_all_three_types}")


if countries_with_all_three_types:
    country_activity_df['Country'] = country_activity_df['Country'].str.strip()
    
    relevant_country_activity = country_activity_df[country_activity_df['Country'].isin(countries_with_all_three_types)]
    top_countries_for_fig2 = relevant_country_activity.sort_values('TOTAL', ascending=False).head(5)['Country'].tolist()
else:
    top_countries_for_fig2 = []

print(f"Top 5 countries (from those with all 3 types) by activity for Fig 2: {top_countries_for_fig2}")

if top_countries_for_fig2:
    top_data_fig2 = combined_data[combined_data['Country'].isin(top_countries_for_fig2)]
    top_avg_fig2 = top_data_fig2.groupby(['Country', 'Category'])['LCOE'].mean().reset_index()

    print("\nAverage LCOE for selected Top Countries (Fig 2):")
    print(top_avg_fig2)

    fig2 = px.bar(
        top_avg_fig2,
        x='Country',
        y='LCOE',
        color='Category',
        title='LCOE Comparison for Top Countries with All Energy Types',
        labels={'LCOE': 'LCOE (USD/MWh)'},
        color_discrete_map={'Nuclear': 'blue', 'Green': 'green', 'Traditional': 'gray'},
        barmode='group',
        category_orders={"Country": top_countries_for_fig2}
    )
    max_lcoe_top_fig2 = top_avg_fig2['LCOE'].max() if not top_avg_fig2.empty else 120
    fig2.update_layout(yaxis_range=[0, max_lcoe_top_fig2 + 20 if pd.notna(max_lcoe_top_fig2) else 120])
    fig2.show()
else:
    print("\nCould not find 5 countries with LCOE data for all three energy types to generate the second plot.")
    if countries_with_all_three_types:
         print(f"Found {len(countries_with_all_three_types)} countries with all three types: {countries_with_all_three_types}. Showing data for these if fewer than 5.")

         if countries_with_all_three_types: 
            top_data_fig2 = combined_data[combined_data['Country'].isin(countries_with_all_three_types)]
            top_avg_fig2 = top_data_fig2.groupby(['Country', 'Category'])['LCOE'].mean().reset_index()
            print("\nAverage LCOE for countries with all three types:")
            print(top_avg_fig2)
            fig2 = px.bar(
                top_avg_fig2,
                x='Country',
                y='LCOE',
                color='Category',
                title=f'LCOE Comparison for Countries with All Energy Types ({len(countries_with_all_three_types)} found)',
                labels={'LCOE': 'LCOE (USD/MWh)'},
                color_discrete_map={'Nuclear': 'blue', 'Green': 'green', 'Traditional': 'gray'},
                barmode='group',
                category_orders={"Country": countries_with_all_three_types} 
            )
            max_lcoe_top_fig2 = top_avg_fig2['LCOE'].max() if not top_avg_fig2.empty else 120
            fig2.update_layout(yaxis_range=[0, max_lcoe_top_fig2 + 20 if pd.notna(max_lcoe_top_fig2) else 120])
            fig2.show()