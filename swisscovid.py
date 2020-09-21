"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
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
# df = pd.read_csv('D:\Programming\SwissCovid\COVID19_Fallzahlen_CH_total.csv')

df_zh = df[df.abbreviation_canton_and_fl == 'ZH']
#print(df_zh)

st.markdown("### Covid-19 Dashboard for Switzerland")

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

# multiselect option to select cantons, could potentially be sorted
cantons = st.multiselect("Which canton(s) are you interested in?", list(canton_dict.keys()))

# dict comprehension to make list out of values from selected keys (cantons)
selected_cantons = [canton_dict[k] for k in cantons if k in canton_dict]
#selected_cantons = ["ZH", "BE"]
# show for debugging purposes
st.write(selected_cantons)

# dataframe with only selected cantons
selected_cantons_df = df.loc[df['abbreviation_canton_and_fl'].isin(selected_cantons)]

# show for debugging purposes
st.write(selected_cantons_df)

# create datetime series from first date to last date
# not necessary
# date_beginning = sorted(df["date"])
# date_beginning = date_beginning[0]
# date_end = sorted(df["date"])
# date_end = date_end[-1]
# full_time_range =  pd.date_range(start=date_beginning, end=date_end, freq="D")

# plotting the line for each selected canton 
for num_cantons, cant in enumerate(selected_cantons): 
    # add missing dates
    #selected_cantons_df.merge(full_time_range.rename('full_date'), how = "right", left_on="date")
    plt.plot(selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date, 
             #selected_cantons_df.ncumul_tested, 
             selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].ncumul_conf, 
             label = cant)

# set x axis label
plt.xlabel('Date')
# set y axis label of the current axis
plt.ylabel('Confirmed cases (cumulative)')
# set a title for the plot
plt.title('Number of confirmed cases (cumulative)')
# show a legend on the plot
plt.legend()
# display tge figure
st.pyplot()

