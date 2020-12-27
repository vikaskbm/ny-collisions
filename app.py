import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import os
from urllib.request import urlretrieve

DATA_URL = 'Motor_Vehicle_Collisions_-_Crashes.csv'

if not os.path.isfile(DATA_URL):
    urlretrieve('https://data.cityofnewyork.us/api/views/h9gi-nx95/rows.csv?accessType=DOWNLOAD')

st.title('New York Vehicle Collision Analysis')
st.markdown('This web app is a streamlit dashboard to analyse and plot motor vehicle collision data')

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH DATE', 'CRASH TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    data.columns = [x.replace(' ', '_') for x in data.columns]

    lowercase = lambda x: str(x).lower()

    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns = {'crash_date_crash_time': 'date/time'}, inplace=True)

    return data

data=load_data(3000)
original_data = data
# st.write(data.columns)

st.header("Where are most people injured?")
injured_people = st.slider("Number of people injured in vehicle collision", 0, 19)
st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many collisions occur during a particular hour?")
hour = st.slider("Hour to look at ", 0, 23)
data = data[data['date/time'].dt.hour==hour]
st.markdown(f"Collisions between {hour}:00 and {hour+1}:00")

midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))

st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 55,
    },

    layers = [
        pdk.Layer(
        'HexagonLayer',
        data=data[["date/time", "latitude", "longitude"]],
        get_position=['longitude',"latitude,"],
        auto_highlight=True,
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],

    )]
))

if st.checkbox('Show RAW data', False):
    st.subheader("Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
    st.write(data)


st.subheader(f"Breakdown by minute bewtween {hour}:00 and {hour+1}:00")
filtered = data[
    (data["date/time"].dt.hour >= hour) & (data["date/time"].dt.hour < (hour + 1))
]   
hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=[0,60])[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected class")
select = st.selectbox('Affected Class', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query('number_of_pedestrians_injured >= 1')[['on_street_name', 'number_of_pedestrians_injured']].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how="any")[:5])
elif select == 'Cyclists':
    st.write(original_data.query('number_of_cyclist_injured >= 1')[['on_street_name', 'number_of_cyclist_injured']].sort_values(by=['number_of_cyclist_injured'], ascending=False).dropna(how="any")[:5])
else :
    st.write(original_data.query('number_of_motorist_injured >= 1')[['on_street_name', 'number_of_motorist_injured']].sort_values(by=['number_of_motorist_injured'], ascending=False).dropna(how="any")[:5])
    
