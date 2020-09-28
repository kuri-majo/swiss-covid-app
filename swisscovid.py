"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

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
    #df = pd.read_excel('https://www.bfs.admin.ch/bfsstatic/dam/assets/11587762/master/je-d-21.03.02.xlsx')
    df = pd.read_excel('je-d-21.03.02.xlsx', skiprows = 3).rename(columns={"Unnamed: 0":"Indicator"}) # canton names are in row 4
    df = df[df["Indicator"].str.contains("Einwohner in 1000", na = False)]
    df = df.transpose() # now, cantons are the row index
    df = df.iloc[3:] # first three rows do not contain cantons
    df = df.div(1000) # first in 1000, now in 100000
    df.columns = ['Inhabitants_100000']
    return df

inhabitants_cantons = load_data_cantons()

# join inhabitant number info with covid data
df = pd.merge(df, inhabitants_cantons, left_on = "abbreviation_canton_and_fl", right_index = True, 
         how = "left")

df["cases_per_100000_inhabitants"] = np.divide(df["ncumul_conf"], df["Inhabitants_100000"])

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
#selected_cantons = ["ZH", "BE"]
# show for debugging purposes
st.write(selected_cantons)

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

# # plotting the line of cumulated cases for each selected canton 
# plt.figure(0)
# for num_cantons, cant in enumerate(selected_cantons): 
#     # add missing dates
#     #selected_cantons_df.merge(full_time_range.rename('full_date'), how = "right", left_on="date")
#     plt.plot(selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date, 
#               #selected_cantons_df.ncumul_tested, 
#               selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].ncumul_conf, 
#               label = cant)

# if selected_cantons: 
#     plt.axvline(x = pd.to_datetime("Mar 16, 2020"), ymin = 0, ymax = 1, label='Beginning of lockdown', 
#                 linestyle = "dotted")
#     plt.axvline(x = pd.to_datetime("Mar 16, 2020") + datetime.timedelta(days=14), ymin = 0, 
#                 ymax = 1, label='Two weeks after lockdown', linestyle = "dotted")

# # set x axis label
# plt.xlabel('Date')
# # set y axis label of the current axis
# plt.ylabel('Confirmed cases (cumulative)')
# # set a title for the plot
# plt.title('Number of confirmed cases (cumulative)')
# # show a legend on the plot
# plt.legend()
# # display the figure
# st.pyplot()

# # plotting the line of cumulated cases per 100000 inhabitants for each selected canton
# plt.figure(1) 
# for num_cantons, cant in enumerate(selected_cantons): 
#     # add missing dates
#     #selected_cantons_df.merge(full_time_range.rename('full_date'), how = "right", left_on="date")
#     plt.plot(selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date, 
#               #selected_cantons_df.ncumul_tested, 
#               selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].cases_per_100000_inhabitants, 
#               label = cant)
# # set x axis label
# plt.xlabel('Date')
# # set y axis label of the current axis
# plt.ylabel('Confirmed cases per 100\'000 inhabitants (cumulative)')
# # set a title for the plot
# plt.title('Number of confirmed cases per 100\'000 inhabitants (cumulative)')
# # show a legend on the plot
# plt.legend()
# # display the figure
# st.pyplot()

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
              selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].cases_per_100000_inhabitants, 
              label = cant)

axs[1].set_title("Per 100\'000 inhabitants")
axs[1].set_xlabel("Date")
# legend
handles, labels = axs[1].get_legend_handles_labels()
fig.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left')
# display the figure
st.pyplot(fig)