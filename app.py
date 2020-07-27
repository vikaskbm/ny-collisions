import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = 'collisions.csv.csv'

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
st.write(data.columns)

