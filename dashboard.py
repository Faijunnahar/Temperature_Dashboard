import streamlit as st
import pandas as pd
import plotly.express as px
import datetime


# Set page title and favicon
st.set_page_config(
    page_title="Climate Data Dashboard",
    page_icon="🌍",
)

# Load the data
data = pd.read_csv('your_dataset.csv')

# Display the title and some introductory text
st.title("Climate Data Dashboard")
st.markdown("Explore and analyze climate data with interactive visualizations.")

# Melt the data to make it suitable for visualization
melted_data = pd.melt(data, id_vars=['ObjectId', 'Country', 'ISO2', 'ISO3', 'Indicator', 'Unit', 'Source', 'CTS_Code', 'CTS_Name', 'CTS_Full_Descriptor'],
                      var_name='Year', value_name='Temperature Change')

# Convert 'Year' column to numeric (remove 'F' prefix)
melted_data['Year'] = melted_data['Year'].str.extract('(\d+)').astype(float)

# Convert 'Temperature Change' column to numeric, replacing non-numeric values with NaN
melted_data['Temperature Change'] = pd.to_numeric(melted_data['Temperature Change'], errors='coerce')

# Sidebar: Date range selection
years = melted_data['Year'].unique()
default_start_date = datetime.date(int(min(years)), 1, 1)
default_end_date = datetime.date(int(max(years)), 12, 31)
date_range = st.sidebar.date_input('Select Date Range', [default_start_date, default_end_date])

# Feature 1: Filter data based on selected date range
filtered_data = melted_data[(melted_data['Year'] >= date_range[0].year) & (melted_data['Year'] <= date_range[1].year)]

# Feature 2: Multiselect for selecting countries
selected_countries = st.sidebar.multiselect('Select Countries', melted_data['Country'].unique())

# Feature 3: Filter data based on selected countries
filtered_data = filtered_data[filtered_data['Country'].isin(selected_countries)]

# Feature 4: Dropdown for selecting indicators
selected_indicator = st.sidebar.selectbox('Select Indicator', melted_data['Indicator'].unique())
filtered_data = filtered_data[filtered_data['Indicator'] == selected_indicator]

# Feature 5: Plotly Choropleth map
fig_map = px.choropleth(filtered_data, locations='ISO3', color='Temperature Change', hover_name='Country',
                        animation_frame='Year', projection='natural earth')

# Feature 6: Heatmap for temperature change across countries
fig_heatmap = px.imshow(filtered_data.pivot_table(index='Country', columns='Year', values='Temperature Change'),
                        labels=dict(color='Temperature Change'), x=filtered_data['Year'].unique(), y=filtered_data['Country'].unique(),
                        title='Temperature Change Across Countries Over Time', aspect='auto')

# Feature 7: Scatter plot for the relationship between two selected countries
if len(selected_countries) == 2:
    fig_scatter = px.scatter(filtered_data, x='Temperature Change', y='Country', color='Country',
                             title=f'Temperature Change Comparison: {selected_countries[0]} vs {selected_countries[1]}')
    st.plotly_chart(fig_scatter)
else:
    st.markdown('<p class="warning-message">Select exactly 2 countries to compare in the scatter plot.</p>', unsafe_allow_html=True)

# Feature 8: Additional filter for temperature range
temperature_min = float(filtered_data['Temperature Change'].min())
temperature_max = float(filtered_data['Temperature Change'].max())
initial_temperature_range = (temperature_min, temperature_max)

# Check for NaN values and set default values
if pd.isna(initial_temperature_range[0]) or pd.isna(initial_temperature_range[1]):
    initial_temperature_range = (0.0, 1.0)  # Set default values if NaN

# Sort the initial values
initial_temperature_range = sorted(initial_temperature_range)

temperature_range = st.sidebar.slider('Select Temperature Range', min_value=temperature_min, max_value=temperature_max,
                                      value=initial_temperature_range, step=0.1)

filtered_data = filtered_data[(filtered_data['Temperature Change'] >= temperature_range[0]) & (filtered_data['Temperature Change'] <= temperature_range[1])]

# Feature 9: Data Export
download_link = 'https://drive.google.com/file/d/1TDMHWqFrIBug83vrt1cyX7lfBgjNenhC/view?usp=drive_link'
if st.sidebar.button('Export Data'):
    st.sidebar.markdown(f'<a href="{download_link}" target="_blank">Download Data</a>', unsafe_allow_html=True)

# Feature 10: Display statistical measures
st.sidebar.subheader('Statistical Measures')
st.sidebar.text(f"Mean Temperature Change: {filtered_data['Temperature Change'].mean()}")
st.sidebar.text(f"Median Temperature Change: {filtered_data['Temperature Change'].median()}")
st.sidebar.text(f"Standard Deviation: {filtered_data['Temperature Change'].std()}")
st.sidebar.text(f"Max Temperature Change: {filtered_data['Temperature Change'].max()}")
st.sidebar.text(f"Min Temperature Change: {filtered_data['Temperature Change'].min()}")

# Feature 11: Time Series Plot
fig_time_series = px.line(filtered_data, x='Year', y='Temperature Change', color='Country',
                          labels={'Temperature Change': 'Temperature Change (°C)'},
                          title='Time Series Plot: Temperature Change Over Time Across Countries')

# Display the time series plot
st.plotly_chart(fig_time_series)

# Feature 12: Data Aggregation
aggregation_level = st.sidebar.selectbox('Select Aggregation Level', ['Country', 'Region', 'Continent'])

# Create a mapping between countries and their corresponding regions/continents
actual_region_mapping = {
    'Afghanistan, Islamic Rep. of': 'Asia',
    'Albania': 'Europe',
    'Algeria': 'Africa',
    # Add more countries and regions
}

# Add a new column for the selected aggregation level
filtered_data['Aggregated'] = filtered_data['Country'].map(actual_region_mapping)

# Function to calculate the mean, handling non-numeric values
def custom_mean(series):
    try:
        return pd.to_numeric(series).mean()
    except Exception as e:
        return None

# Aggregate data based on the selected level
aggregated_data = filtered_data.groupby(['Aggregated', 'Year'])['Temperature Change'].agg(custom_mean).reset_index()

# Plot aggregated data as a line chart
fig_aggregated = px.line(aggregated_data, x='Year', y='Temperature Change', color='Aggregated',
                         labels={'Temperature Change': 'Mean Temperature Change (°C)'},
                         title=f'Aggregated Temperature Change Over Time by {aggregation_level}')

# Display the aggregated time series plot
st.plotly_chart(fig_aggregated)


# Display the heatmap
st.plotly_chart(fig_heatmap)

# Display the map
st.plotly_chart(fig_map)

# Show the melted data (for debugging purposes)
st.dataframe(filtered_data)
