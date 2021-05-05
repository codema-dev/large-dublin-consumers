
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


st.title("Dublin Large Energy Consumers")

df = pd.read_csv("data/top_200_building_demands.csv")
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

map_data = gdf[["building_type", "inferred_energy_mwh_per_year", "Benchmark", "address", "latitude", "longitude"]]

st.map(map_data)