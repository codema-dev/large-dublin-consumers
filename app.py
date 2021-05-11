
from pathlib import Path
from typing import List
from typing import Tuple

import geopandas as gpd
from geopandas import GeoDataFrame
import numpy as np
import pandas as pd
from pandas import DataFrame
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt

import glob
import pygeos
import rtree
import pandas_bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.plotting import gmap
from bokeh.models import ColumnDataSource, CustomJS
from shapely.geometry import Point
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models import ColumnDataSource
import fiona


st.title("Dublin Large Energy Consumers")

df = pd.read_csv("data/top_200_building_demands.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

map_data = gdf[["building_type", "inferred_energy_mwh_per_year", "Benchmark", "address", "latitude", "longitude", "geometry"]]
map_data = map_data.set_crs(epsg="4326")

pd.set_option('plotting.backend', 'pandas_bokeh')
pandas_bokeh.output_notebook()

st.map(map_data)

hovertool_string=("""
<table>
    <tr>
        <th>Energy Demand (MWh/year)</th>
        <td>@inferred_energy_mwh_per_year</td>
    </tr>
</table>""")

bokeh_fig = map_data.plot_bokeh(hovertool_string=hovertool_string)

st.bokeh_chart(bokeh_fig)

