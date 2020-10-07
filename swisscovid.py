""" Swiss Covid Dashboard.
Longer description of this module.
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Ira Kurthen"
__contact__ = "ira.kurthen[at]gmail.com"
__date__ = "2020/10/03"
__deprecated__ = False
__license__ = "GPLv3"
__version__ = "0.0.3"

import numpy as np
import pandas as pd
#import datetime
#import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go

@st.cache
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total.csv', 
                     parse_dates = ["date"])
    return df

df = load_data()
#print(df)
# df = pd.read_csv('D:\Programming\swiss-covid-app\COVID19_Fallzahlen_CH_total.csv')

st.title("Covid-19 Dashboard for Switzerland")
st.markdown("This is a dashboard made for exploring how the Swiss cantons "
            "differ in Covid-19 caseload. It has been programmed by " 
            "[Ira Kurthen](https://datamahou.ch/cv/) " 
            "and it uses open data provided by " 
            "[Statistisches Amt Kanton Zürich](https://github.com/openZH/covid_19).")
st.markdown("The code for this dashboard can be found on my [GitHub](https://github.com/kuri-majo/swiss-covid-app). "
            "The dashboard was programmed using [Streamlit](https://www.streamlit.io/) "
            "and is hosted on an SSL-secured [DigitalOcean](https://www.digitalocean.com/) droplet "
            "served by [nginx](https://www.nginx.com/).")
st.markdown('To get started...')

# inhabitants per canton
@st.cache
def load_data_cantons():
    #df = pd.read_excel('https://www.bfs.admin.ch/bfsstatic/dam/assets/11587762/master/je-d-21.03.02.xlsx', skiprows = 3).rename(columns={"Unnamed: 0":"Indicator"}) # canton names are in row 4
    df = pd.read_excel('je-d-21.03.02.xlsx', skiprows = 3).rename(columns={"Unnamed: 0":"Indicator"}) # canton names are in row 4
    df = df[df["Indicator"].str.contains("Einwohner in 1000", na = False)]
    df = df.transpose() # now, cantons are the row index
    df = df.iloc[3:] # first three rows do not contain cantons
    #df = df.div(1000) # first in 1000, now in 100000
    df.columns = ['Inhabitants_1000']
    return df

inhabitants_cantons = load_data_cantons()

# join inhabitant number info with covid data
df = pd.merge(df, inhabitants_cantons, left_on = "abbreviation_canton_and_fl", right_index = True, 
         how = "left")

df["cases_per_1000_inhabitants"] = np.divide(df["ncumul_conf"], df["Inhabitants_1000"])

# canton abbreviations are used in the dataset, so we need to know these abbreviations
canton_dict = {
    "Zürich": "ZH", 
	"Bern": "BE", 
    "Luzern": "LU", 
    "Uri": "UR", 
    "Schwyz": "SZ", 
	"Obwalden": "OW", 
    "Nidwalden": "NW",
    "Glarus": "GL",
	"Zug": "ZG",
	"Fribourg": "FR",
	"Solothurn": "SO",
	"Basel-Stadt": "BS",
	"Basel-Landschaft": "BL",
	"Schaffhausen": "SH",
	"Appenzell Ausserrhoden": "AR",
	"Appenzell Innerrhoden": "AI",
	"St. Gallen": "SG",
	"Graubünden": "GR",
	"Aargau": "AG",
	"Thurgau": "TG",
	"Ticino": "TI",
	"Vaud": "VD",
	"Valais": "VS",
	"Neuchâtel": "NE", 
	"Geneva": "GE", 
	"Jura": "JU"}

# heading canton selection
st.header("Select the cantons you wish to compare.")

# multiselect option to select sorted cantons
cantons = st.multiselect("Which canton(s) are you interested in?", sorted(list(canton_dict.keys())))

# dict comprehension to make list out of values from selected keys (cantons)
selected_cantons = [canton_dict[k] for k in cantons if k in canton_dict]
#selected_cantons = ["ZH", "BE"] # just for testing

# dataframe with only selected cantons
selected_cantons_df = df.loc[df['abbreviation_canton_and_fl'].isin(selected_cantons)]
# show for debugging purposes
#st.write(selected_cantons_df)

# add possibility of switching to log y axis

log_y_axis = st.selectbox(
    'Y-axis: linear or logarithmic?',
     ['linear', 'logarithmic'])

# to do: make function out of this
if 1: # plotly version
    # Create traces
    fig_total_cases = go.Figure()
    for num_cantons, cant in enumerate(selected_cantons): 
        fig_total_cases.add_trace(go.Scatter(
            x = selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date,
            y = selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].ncumul_conf,
            mode = 'lines',
            name = cant, 
            line_shape = 'linear')) # linear interpolation of missing data
    fig_total_cases.update_layout(template = 'plotly_white', 
                      title="Number of confirmed cases (cumulative)",
                      xaxis_title="Date",
                      yaxis_title="Confirmed Cases",
                      legend_title="Canton", 
                      xaxis_fixedrange = True, # disable zooming/panning, useful for mobile screens
                      yaxis_fixedrange = True, # disable zooming/panning, useful for mobile screens
                      showlegend = True) # always show legend, even if only one canton is selected
    if log_y_axis == 'logarithmic':
        fig_total_cases.update_yaxes(type="log")
    st.plotly_chart(fig_total_cases, use_container_width = True) # use container width allows for mobile screens
    
    fig_per_number = go.Figure()
    for num_cantons, cant in enumerate(selected_cantons): 
        fig_per_number.add_trace(go.Scatter(
            x = selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date,
            y = selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].cases_per_1000_inhabitants,
            mode = 'lines',
            name = cant, 
            line_shape = 'linear')) # linear interpolation of missing data
    fig_per_number.update_layout(template = 'plotly_white', 
                      title="Number of confirmed cases per 1000 inhabitants (cumulative)",
                      xaxis_title="Date",
                      yaxis_title="Confirmed cases per 1000 inhabitants (cumulative)",
                      legend_title="Canton", 
                      xaxis_fixedrange = True, # disable zooming/panning, useful for mobile screens
                      yaxis_fixedrange = True, # disable zooming/panning, useful for mobile screens
                      showlegend = True) # always show legend, even if only one canton is selected
    if log_y_axis == 'logarithmic':
        fig_per_number.update_yaxes(type="log")
    st.plotly_chart(fig_per_number, use_container_width = True) # use container width allows for mobile screens

# show raw data if asked
show_raw_data = st.checkbox('Show raw data', value = False)

if show_raw_data: 
    st.write(df)