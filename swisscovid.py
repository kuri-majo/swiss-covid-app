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
import datetime
import matplotlib.pyplot as plt
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

st.markdown("### Covid-19 Dashboard for Switzerland")

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

show_raw_data = st.checkbox('Show raw data', value = False)

if show_raw_data: 
    st.write(df)

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

# multiselect option to select sorted cantons
cantons = st.multiselect("Which canton(s) are you interested in?", sorted(list(canton_dict.keys())))

# dict comprehension to make list out of values from selected keys (cantons)
selected_cantons = [canton_dict[k] for k in cantons if k in canton_dict]
#selected_cantons = ["ZH", "BE"] # just for testing

# dataframe with only selected cantons
selected_cantons_df = df.loc[df['abbreviation_canton_and_fl'].isin(selected_cantons)]
# show for debugging purposes
#st.write(selected_cantons_df)

# create datetime series from first date to last date
# not necessary
# date_beginning = sorted(df["date"])
# date_beginning = date_beginning[0]
# date_end = sorted(df["date"])
# date_end = date_end[-1]
# full_time_range =  pd.date_range(start=date_beginning, end=date_end, freq="D")

if 0: #matplotlib two plots version
    # plotting the line of cumulated cases for each selected canton 
    plt.figure(0)
    for num_cantons, cant in enumerate(selected_cantons): 
        # add missing dates
        #selected_cantons_df.merge(full_time_range.rename('full_date'), how = "right", left_on="date")
        plt.plot(selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date, 
                  #selected_cantons_df.ncumul_tested, 
                  selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].ncumul_conf, 
                  label = cant)
    
    if selected_cantons: 
        plt.axvline(x = pd.to_datetime("Mar 16, 2020"), ymin = 0, ymax = 1, label='Beginning of lockdown', 
                    linestyle = "dotted")
        plt.axvline(x = pd.to_datetime("Mar 16, 2020") + datetime.timedelta(days=14), ymin = 0, 
                    ymax = 1, label='Two weeks after lockdown', linestyle = "dotted")
    
    # set x axis label
    plt.xlabel('Date')
    # set y axis label of the current axis
    plt.ylabel('Confirmed cases (cumulative)')
    # set a title for the plot
    plt.title('Number of confirmed cases (cumulative)')
    # show a legend on the plot
    plt.legend()
    # display the figure
    st.pyplot()
    
    # plotting the line of cumulated cases per 1000 inhabitants for each selected canton
    plt.figure(1) 
    for num_cantons, cant in enumerate(selected_cantons): 
        # add missing dates
        #selected_cantons_df.merge(full_time_range.rename('full_date'), how = "right", left_on="date")
        plt.plot(selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date, 
                  #selected_cantons_df.ncumul_tested, 
                  selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].cases_per_1000_inhabitants, 
                  label = cant)
    # set x axis label
    plt.xlabel('Date')
    # set y axis label of the current axis
    plt.ylabel('Confirmed cases per 1000 inhabitants (cumulative)')
    # set a title for the plot
    plt.title('Number of confirmed cases per 1000 inhabitants (cumulative)')
    # show a legend on the plot
    plt.legend()
    # display the figure
    st.pyplot()

if 0: # matplotlib subplot version
    # subplot version
    fig, axs = plt.subplots(2, sharex = True)
    fig.suptitle('Cumulative Covid Cases')
    
    for num_cantons, cant in enumerate(selected_cantons): 
        # add missing dates
        #selected_cantons_df.merge(full_time_range.rename('full_date'), how = "right", left_on="date")
        axs[0].plot(selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date, 
                  #selected_cantons_df.ncumul_tested, 
                  selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].ncumul_conf, 
                  label = cant)
    
    axs[0].set_title("Total")
    
    for num_cantons, cant in enumerate(selected_cantons): 
        # add missing dates
        #selected_cantons_df.merge(full_time_range.rename('full_date'), how = "right", left_on="date")
        axs[1].plot(selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date, 
                  #selected_cantons_df.ncumul_tested, 
                  selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].cases_per_1000_inhabitants, 
                  label = cant)
    
    axs[1].set_title("Per 1000 inhabitants")
    axs[1].set_xlabel("Date")
    # legend
    handles, labels = axs[1].get_legend_handles_labels()
    fig.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left')
    # increases whitespace between subplots
    fig.tight_layout(pad=3.0)
    # display the figure
    st.pyplot(fig)

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
                      showlegend = True) # always show legend, even if only one canton is selected
    st.write(fig_total_cases)
    
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
                      showlegend = True) # always show legend, even if only one canton is selected
    st.write(fig_per_number)