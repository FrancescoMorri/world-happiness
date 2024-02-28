import pydeck as pdk
import pandas as pd
import geopandas as gpd
import streamlit as st
import json
import numpy as np
import altair as alt

@st.cache(allow_output_mutation=True)
def load_data(PATH, H_PATH):
    geo_data = gpd.read_file(PATH)[['name','geometry']]
    h_data = pd.read_csv(H_PATH)[['Country','Happiness score','Rank']]
    h_data.columns = ['Country', 'h_score', 'rank']
    merged = geo_data.merge(h_data, left_on='name', right_on='Country')
    merged.drop(['Country'], axis='columns', inplace=True)
    merged['normal'] = (merged['h_score']-merged['h_score'].min())/(merged['h_score'].max()-merged['h_score'].min())
    merged['elevation'] = abs(merged['rank']-merged['rank'].max())
    #merged_json = json.loads(merged.to_json())
    return merged

with open('graph_data.json') as f:
    plot_data = json.load(f)


st.set_page_config(page_title='Happiness Score', page_icon="🗺️", layout="wide")
st.title("Happiness Score Around the World through the Years")
st.caption("Data from the Happiness Report plotted on the globe. The more blue a nation is, the happiest is supposed to be. Conversely, more red means less happiness. After the map it is possible to confront the evolution in time of happiness for different nations.")

year = st.select_slider("Year", options=['2015','2016','2017','2018','2019','2020','2021','2022'])



PATH = "world-administrative-boundaries/world-administrative-boundaries.shp"
H_PATH = "archive/"+str(year)+".csv"

pdk_data = load_data(PATH=PATH, H_PATH=H_PATH)

geojson = pdk.Layer(
    'GeoJsonLayer',
    pdk_data,
    opacity=0.5,
    filled=True,
    extruded=True,
    wireframe=True,
    auto_highlight=True,
    get_elevation='elevation*3000',
    get_fill_color='[(1-normal)*255,100,normal*255]',
    pickable=True
)

INITIAL_VIEW_STATE = pdk.ViewState(
    latitude=0,
    longitude=0,
    zoom=1.5,
    max_zoom=16,
    pitch=45,
    bearing=0
)

r = pdk.Deck(
    layers=[geojson],
    initial_view_state=INITIAL_VIEW_STATE,
    tooltip={"text":'{name}\n Happiness rank: {rank}'})

st.pydeck_chart(r)

st.header("Graph of ranking through time")
with st.form("Select nations"):
    nations = st.multiselect("Nations", plot_data.keys())
    measure = st.selectbox("Ranking or Happines Score?",['rank','score'])
    submitted = st.form_submit_button('Plot')

if submitted:
    pd_data = pd.DataFrame(columns=['name','date','rank','score'])
    for n in nations:
        for e in plot_data[n]:
            pd_data.loc[len(pd_data)] = [n,e[0],e[1],e[2]]
    
    g = alt.Chart(pd_data).mark_line().encode(
            x='date',
            y=alt.Y(measure,scale=alt.Scale(domain=[pd_data[measure].min(), pd_data[measure].max()])),
            color='name'
        ).configure_axis(
            labelFontSize=20,
            titleFontSize=20
        ).configure_legend(
            labelFontSize=20,
            titleFontSize=20
        ).interactive()
    st.altair_chart(g, use_container_width=True)

st.header("Full Ranking")
with st.form("Full Ranking"):
    year = st.selectbox("Select a year", ['2015','2016','2017','2018','2019','2020','2021','2022'])
    submit = st.form_submit_button("Show List")

if submit:
    data = pd.read_csv("archive/"+str(year)+".csv")[['Country','Rank','Happiness score']]
    data = data.sort_values(by=['Rank'])
    st.dataframe(data,width=500)

      
