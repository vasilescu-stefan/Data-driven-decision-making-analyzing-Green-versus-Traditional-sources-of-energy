

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Load Country Activity Data (Table 1.1) ---
# The header 'Country,Natural gas,...TOTAL' is on the 4th line of the CSV snippet, so skiprows=3
country_activity_df = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\1_1.csv', skiprows=3)

country_activity_df['TOTAL'] = pd.to_numeric(country_activity_df['TOTAL'], errors='coerce')
country_activity_df = country_activity_df.dropna(subset=['Country', 'TOTAL'])
# We will determine top_countries later, based on LCOE data availability

# --- Load LCOE Data ---
# Standard approach for LCOE files, assuming skiprows=4 lands you just above data lines,
# and data lines start with an empty field, then country, then other data.
# Country will be at iloc index 1. LCOE needs to be identified carefully.

# Nuclear New Build (Table 3.13.a)
# Data line: ,France,EPR,...,O&M(idx12), LCOE1(idx13), LCOE2(idx14), LCOE3(idx15), France(idx16)
# We want Country (idx 1) and LCOE1 (idx 13)
nuclear_new_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_13_a_b1_b2.csv', skiprows=4) # Assuming this file contains new build
nuclear_new = nuclear_new_temp.iloc[:, [1, 13]].copy()
nuclear_new.columns = ['Country', 'LCOE']
nuclear_new['Category'] = 'Nuclear'

# Nuclear LTO (e.g., from Table 3.13.b1 in the same CSV or a different one)
# Assuming structure similar to new build for relevant columns after skiprows=4
# Data line: ,Switzerland,LTO,...,O&M(idx12), LCOE1(idx13), LCOE2(idx14), LCOE3(idx15), Switzerland(idx16)
# We want Country (idx 1) and LCOE1 (idx 13)
try:
    nuclear_lto_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_22_a_b1_b2.csv', skiprows=4)
    nuclear_lto = nuclear_lto_temp.iloc[:, [1, 13]].copy() # Adjust LCOE index if different
    nuclear_lto.columns = ['Country', 'LCOE']
    nuclear_lto['Category'] = 'Nuclear'
    nuclear = pd.concat([nuclear_new, nuclear_lto])
except FileNotFoundError:
    print("Warning: nuclear_lto file (3_22_a_b1_b2.csv) not found. Using only new build nuclear data.")
    nuclear = nuclear_new # Fallback if LTO file is missing
except IndexError:
    print(f"Warning: Indexing error while processing nuclear_lto file (3_22_a_b1_b2.csv) - check column indices {1, 13}. Using only new build nuclear data.")
    nuclear = nuclear_new


# Solar (Table 3.14)
solar_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_14.csv', skiprows=4)
solar = solar_temp.iloc[:, [1, 14]].copy() # Country (idx 1), LCOE (original idx 14)
solar.columns = ['Country', 'LCOE']
solar['Category'] = 'Green'

# Wind (Table 3.15.a)
wind_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_15_a_b.csv', skiprows=4)
wind = wind_temp.iloc[:, [1, 13]].copy() # Country (idx 1), LCOE (original idx 13)
wind.columns = ['Country', 'LCOE']
wind['Category'] = 'Green'

# Hydro (Table 3.16.a)
hydro_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_16_a_b_c.csv', skiprows=4)
hydro = hydro_temp.iloc[:, [1, 13]].copy() # Country (idx 1), LCOE (original idx 13)
hydro.columns = ['Country', 'LCOE']
hydro['Category'] = 'Green'

green = pd.concat([solar, wind, hydro])

# Coal (Table 3.12 like structure, from 3_21.csv)
# Data line: ,Australia,Tech,...,O&M(idx13), LCOE1(idx14), LCOE2(idx15), LCOE3(idx16), Australia(idx17)
# We want Country (idx 1) and LCOE1 (idx 14)
coal_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_21.csv', skiprows=4)
coal = coal_temp.iloc[:, [1, 14]].copy()
coal.columns = ['Country', 'LCOE']
coal['Category'] = 'Traditional'

# Gas (Table 3.11.a like structure, from 3_20a_b.csv)
# Data line: ,Australia,Tech,...,O&M(idx13), LCOE1(idx14), LCOE2(idx15), LCOE3(idx16), Australia(idx17)
# We want Country (idx 1) and LCOE1 (idx 14)
gas_temp = pd.read_csv(r'Data-Analysis-Between-Traditional-and-Green-sources-of-energy\excel_conversions\3_20a_b.csv', skiprows=4)
gas = gas_temp.iloc[:, [1, 14]].copy()
gas.columns = ['Country', 'LCOE']
gas['Category'] = 'Traditional'

traditional = pd.concat([coal, gas])

# --- Combine and Clean All Data ---
combined_data = pd.concat([nuclear, green, traditional])
combined_data['LCOE'] = pd.to_numeric(combined_data['LCOE'], errors='coerce')
combined_data['Country'] = combined_data['Country'].str.strip() # Clean country names
combined_data = combined_data.dropna(subset=['Country', 'LCOE'])

# --- Compute Global Averages ---
world_avg = combined_data.groupby('Category')['LCOE'].mean().reset_index()
print("\nGlobal Average LCOE by Category:")
print(world_avg)

# --- Plot Global Average LCOE ---
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


# --- Identify Top 5 Countries with All Three Energy Types ---
# 1. Find countries that have data for all 3 categories
country_category_counts = combined_data.groupby('Country')['Category'].nunique()
countries_with_all_three_types = country_category_counts[country_category_counts == 3].index.tolist()

print(f"\nCountries with LCOE data for all 3 energy types: {countries_with_all_three_types}")

# 2. From these countries, select top 5 based on 'TOTAL' activity from country_activity_df
if countries_with_all_three_types:
    # Ensure country names in country_activity_df are also stripped for accurate matching
    country_activity_df['Country'] = country_activity_df['Country'].str.strip()
    
    relevant_country_activity = country_activity_df[country_activity_df['Country'].isin(countries_with_all_three_types)]
    top_countries_for_fig2 = relevant_country_activity.sort_values('TOTAL', ascending=False).head(5)['Country'].tolist()
else:
    top_countries_for_fig2 = []

print(f"Top 5 countries (from those with all 3 types) by activity for Fig 2: {top_countries_for_fig2}")

# --- Filter LCOE Data for These Top Countries and Plot Comparison ---
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
        category_orders={"Country": top_countries_for_fig2} # Ensures consistent order in the plot
    )
    max_lcoe_top_fig2 = top_avg_fig2['LCOE'].max() if not top_avg_fig2.empty else 120
    fig2.update_layout(yaxis_range=[0, max_lcoe_top_fig2 + 20 if pd.notna(max_lcoe_top_fig2) else 120])
    fig2.show()
else:
    print("\nCould not find 5 countries with LCOE data for all three energy types to generate the second plot.")
    if countries_with_all_three_types:
         print(f"Found {len(countries_with_all_three_types)} countries with all three types: {countries_with_all_three_types}. Showing data for these if fewer than 5.")
         # Optionally, you could still plot if you have at least 1 country
         if countries_with_all_three_types: # If any country has all three types
            top_data_fig2 = combined_data[combined_data['Country'].isin(countries_with_all_three_types)] # Use all found countries
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