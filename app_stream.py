
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
import utm

import glob
import pygeos
import rtree
import pandas_bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider, Vendors 
from bokeh.plotting import gmap
from bokeh.models import ColumnDataSource, CustomJS
from shapely.geometry import Point
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models import ColumnDataSource, GMapOptions
import fiona


st.title("Dublin Large Energy Consumers")

df = pd.read_csv("data/top_200_building_demands.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

map_data = gdf[["building_type", "inferred_energy_mwh_per_year", "Benchmark", "address", "latitude", "longitude", "geometry"]]
map_data = map_data.set_crs(epsg="4326")
map_data = map_data.to_crs(epsg="3857")


map_data["x"] = map_data.geometry.apply(lambda row:row.x)
map_data["y"] = map_data.geometry.apply(lambda row:row.y)

map_data = map_data[["building_type", "inferred_energy_mwh_per_year", "Benchmark", "address", "x", "y"]]


st.write(map_data)

source = ColumnDataSource(map_data)
plot = figure(x_axis_type="mercator", y_axis_type="mercator", tools="pan, box_zoom, wheel_zoom, lasso_select")
plot.xaxis.axis_label = 'longitude'
plot.yaxis.axis_label = 'latitude'

tile_provider = get_provider(Vendors.CARTODBPOSITRON)

plot.add_tile(tile_provider)
plot.circle("x", "y", source=source)

source.selected.js_on_change(
    "indices",
    CustomJS(
        args=dict(source=source),
        code="""
        document.dispatchEvent(
            new CustomEvent("LargeConsumers", {detail: {indices: cb_obj.indices}})
        )
        """
    )
)


pd.set_option('plotting.backend', 'pandas_bokeh')
pandas_bokeh.output_notebook()

result = streamlit_bokeh_events(
        bokeh_plot=plot,
        events="LargeConsumers",
        key="foo",
        refresh_on_update=False,
        override_height=600,
        debounce_time=500)


if result is not None:
    # TestSelectEvent was thrown
    if "LargeConsumers" in result:
        st.subheader("Selected Consumers Demand Summary")
        indices = result["LargeConsumers"].get("indices", [])
        st.table(df.iloc[indices].describe())        

# use the result
st.subheader("Raw Consumption Data")
st.write(result)
