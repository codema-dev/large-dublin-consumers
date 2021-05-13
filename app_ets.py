
from typing import List
from bokeh.models.widgets.tables import DataTable

import geopandas as gpd
from geopandas import GeoDataFrame
import pandas as pd
import streamlit as st

import pandas_bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider, Vendors 
from bokeh.plotting import gmap
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models import TableColumn
from streamlit_bokeh_events import streamlit_bokeh_events

st.set_page_config(layout="wide")

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.beta_columns((2,3))

with row1_1:
    st.title("Dublin EPA ETS Sites")

with row1_2:
    st.write(
    """
    ##
    Examining the EPA Emissions Trading Scheme (ETS) buildings across county Dublin, and their relevant 
    Select the Lasso Tool to Extract Data from the Interactive Map.
    """)


# READ IN TOP BUILDINGS DEMANDS
df = pd.read_csv("data/epa_ets_sites_dublin.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

map_data = gdf[["Name", "Installation Name", "License",	"ID", "Address", "metered_annual_emissions_tco2", "estimated_annual_electricity_mwh", "Use", "Latitude", "Longitude", "geometry"]]

map_data = gpd.GeoDataFrame(map_data)

map_data = map_data.set_crs(epsg="4326")
map_data = map_data.to_crs(epsg="3857")

map_data["x"] = map_data.geometry.apply(lambda row:row.x)
map_data["y"] = map_data.geometry.apply(lambda row:row.y)

map_data = map_data[["Name", "Installation Name", "License", "ID", "Address", "metered_annual_emissions_tco2", "estimated_annual_electricity_mwh", "Use", "x", "y"]]

df = map_data

col1, col2 = st.beta_columns(2)

cds = ColumnDataSource(df)

columns = list(map(lambda colname: TableColumn(field=colname, title=colname), df.columns))

cds.selected.js_on_change(
    "indices",
    CustomJS(
        args=dict(source=cds),
        code="""
        document.dispatchEvent(
            new CustomEvent("INDEX_SELECT", {detail: {data: source.selected.indices}})
        )
        """
    )
)

table = DataTable(source=cds, columns=columns)
with col1:
    result = streamlit_bokeh_events(
        bokeh_plot=table,
        events="INDEX_SELECT",
        key="foo",
        refresh_on_update=False,
        debounce_time=0,
        override_height=500
    )
    if result:
        if result.get("INDEX_SELECT"):
            st.write(df.iloc[result.get("INDEX_SELECT")["data"]])

plot = figure(tools="lasso_select,zoom_in", width=250, height=250)
cds_lasso = ColumnDataSource(df)
cds_lasso.selected.js_on_change(
    "indices",
    CustomJS(
        args=dict(source=cds_lasso),
        code="""
        document.dispatchEvent(
            new CustomEvent("LASSO_SELECT", {detail: {data: source.selected.indices}})
        )
        """
    )
)

plot = figure(x_axis_type="mercator", y_axis_type="mercator", tools="pan, box_zoom, wheel_zoom, lasso_select")
plot.xaxis.axis_label = 'longitude'
plot.yaxis.axis_label = 'latitude'

tile_provider = get_provider(CARTODBPOSITRON)

plot.add_tile(tile_provider)
plot.circle("x", "y", fill_alpha=0.5, size=5, line_color=None, source=cds_lasso)
with col2:
    result_lasso = streamlit_bokeh_events(
        bokeh_plot=plot,
        events="LASSO_SELECT",
        key="bar",
        refresh_on_update=False,
        debounce_time=0)
    if result_lasso:
        if result_lasso.get("LASSO_SELECT"):
            st.write(df.iloc[result_lasso.get("LASSO_SELECT")["data"]])