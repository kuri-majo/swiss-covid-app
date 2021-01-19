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
__date__ = "2020/11/22"
__deprecated__ = False
__license__ = "GPLv3"
__version__ = "0.3.0"

import numpy as np
import pandas as pd
import datetime
#import matplotlib.pyplot as plt  # was 3.3.1
import streamlit as st
import plotly.graph_objects as go
import json
import os
#import st_rerun
#import time

# set working directory to file location
os.chdir(os.path.dirname(__file__))

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
	"Genève": "GE", 
	"Jura": "JU"}
# also add a reversed version of the dictionary
rev_canton_dict = {value : key for (key, value) in canton_dict.items()}

@st.cache
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/openZH/covid_19/master/COVID19_Fallzahlen_CH_total.csv', 
                     parse_dates = ["date"])
    df['canton_full_name'] = df['abbreviation_canton_and_fl'].map(rev_canton_dict) # add full canton names
    return df

df = load_data()
#print(df)
# df = pd.read_csv('D:\Programming\swiss-covid-app\COVID19_Fallzahlen_CH_total.csv')

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

# there are missing values for ncumul_conf, we will interpolate them
# need to do this by canton
for cant in df["abbreviation_canton_and_fl"].drop_duplicates():  
    temp_df = df[df["abbreviation_canton_and_fl"] == cant][["date", "abbreviation_canton_and_fl", "ncumul_conf"]].copy()     
    temp_df["ncumul_conf"] = temp_df["ncumul_conf"].interpolate(method = "linear")
    df.update(temp_df)  # modifies in place using non-NA values from another DataFrame. Aligns on indices.

# divide by inhabitants
df["cases_per_1000_inhabitants"] = np.divide(df["ncumul_conf"], df["Inhabitants_1000"])

# calculate new cases per day, this is complicated because of cantons
df["new_cases_per_day_unsmoothed"] = np.nan
df["new_cases_per_day"] = np.nan
for cant in df["abbreviation_canton_and_fl"].drop_duplicates():  
    temp_df = df[df["abbreviation_canton_and_fl"] == cant][["date", "abbreviation_canton_and_fl", "ncumul_conf"]].copy()     
    temp_df["new_cases_per_day_unsmoothed"] = temp_df["ncumul_conf"] - temp_df["ncumul_conf"].shift()
    temp_df['new_cases_per_day'] = temp_df['new_cases_per_day_unsmoothed'].rolling(7).mean()
    df.update(temp_df)  # modifies in place using non-NA values from another DataFrame. Aligns on indices.

df["new_cases_per_1000_inhabitants"] = np.divide(df["new_cases_per_day"], df["Inhabitants_1000"])

# read from geojson, necessary for plotly choropleth maps
with open("CHE_adm1.geojson", encoding="latin1") as geofile:
    cantons_jsonfile = json.load(geofile)

# some naming problems, need to adjust manually
cantons_jsonfile["features"][11]["properties"]["NAME_1"] = "Luzern"
cantons_jsonfile["features"][15]["properties"]["NAME_1"] = "St. Gallen"

analysis = st.sidebar.selectbox('Select an Option', 
                                ['Welcome Page', 
                                 'New Cases per Day', 
                                 'Cumulative Cases'])


# slider for date filtering
# from here: https://towardsdatascience.com/creating-an-interactive-datetime-filter-with-pandas-and-streamlit-2f6818e90aed
def df_filter(message, df):

        slider_1, slider_2 = st.slider('%s' % (message),0,len(df)-1,[0,len(df)-1],1)

        while len(str(df.iloc[slider_1][1]).replace('.0','')) < 4:
            df.iloc[slider_1,1] = '0' + str(df.iloc[slider_1][1]).replace('.0','')
            
        while len(str(df.iloc[slider_2][1]).replace('.0','')) < 4:
            df.iloc[slider_2,1] = '0' + str(df.iloc[slider_1][1]).replace('.0','')

        start_date = datetime.datetime.strptime(str(df.iloc[slider_1][0]).replace('.0',''), "%Y-%m-%d %H:%M:%S")
        start_date = start_date.strftime('%d %b %Y, %I:%M%p')
        
        end_date = datetime.datetime.strptime(str(df.iloc[slider_2][0]).replace('.0',''), "%Y-%m-%d %H:%M:%S")
        end_date = end_date.strftime('%d %b %Y, %I:%M%p')

        st.info('Start: **%s** End: **%s**' % (start_date,end_date))
        
        filtered_df = df.iloc[slider_1:slider_2+1][:].reset_index(drop=True)

        return filtered_df


# generic function to display options for plotting
def display_plot_options(): 
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
    
   # selected_cantons_df = df_filter('Move sliders to filter dataframe', selected_cantons_df)
        
    # add possibility of switching to log y axis
    log_y_axis = st.selectbox(
        'Y-axis: linear or logarithmic?',
         ['linear', 'logarithmic'])
    return selected_cantons, selected_cantons_df, log_y_axis

# generic function for time series plotting
def plot_covid_time_series(col): 
    fig = go.Figure()
    for num_cantons, cant in enumerate(selected_cantons): 
        fig.add_trace(go.Scatter(
            x = selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant].date,
            y = selected_cantons_df[selected_cantons_df['abbreviation_canton_and_fl'] == cant][col],
            mode = 'lines',
            name = cant, 
            line_shape = 'linear')) # linear interpolation of missing data
        if col == "ncumul_conf": 
            title = "Number of confirmed cases (cumulative)"
        elif col == "cases_per_1000_inhabitants": 
            title = "Confirmed cases per 1000 inhabitants (cumulative)"
        elif col == "new_cases_per_day": 
            title = "Number of new confirmed cases"
        elif col == "new_cases_per_1000_inhabitants": 
            title = "New confirmed cases per 1000 inhabitants"
        else: 
            title = ""
            
        fig.update_layout(template = 'plotly_white', 
                          title = title,
                          xaxis_title="Date",
                          yaxis_title="Confirmed Cases",
                          legend_title="Canton", 
                          xaxis_fixedrange = True, # disable zooming/panning, useful for mobile screens
                          yaxis_fixedrange = True, # disable zooming/panning, useful for mobile screens
                          showlegend = True) # always show legend, even if only one canton is selected
        if log_y_axis == 'logarithmic':
            fig.update_yaxes(type="log")
    st.plotly_chart(fig, use_container_width = True) # use container width allows for mobile screens


if analysis == 'Welcome Page':
    # text in the beginning
    if 1:
        st.title("Covid-19 Dashboard for Switzerland")
        st.markdown("This is a dashboard made for exploring how the Swiss cantons "
                    "differ in Covid-19 caseload. It has been programmed by " 
                    "[Ira Kurthen](https://datamahou.ch/cv/) " 
                    "and it uses open data provided by " 
                    "[Statistisches Amt Kanton Zürich](https://github.com/openZH/covid_19).")
        st.markdown("This welcome page displays an interactive map of the Swiss cantons. "
                    "Please move the cursor over a canton to see its current caseload. "
                    "Use the sidebar on the left to navigate to pages that allow you "
                    "to select cantons for comparisons regarding new and cumulative cases.")
        
        st.markdown("The code for this dashboard can be found on my [GitHub](https://github.com/kuri-majo/swiss-covid-app). "
                    "The dashboard was programmed using [Streamlit](https://www.streamlit.io/) "
                    "and is hosted on an SSL-secured [DigitalOcean](https://www.digitalocean.com/) droplet "
                    "served by [nginx](https://www.nginx.com/).")
        #st.markdown('To get started...')
    
    
    # initialize choropleth map
    fig = go.Figure(data = go.Choroplethmapbox(
        geojson = cantons_jsonfile, 
        z = df["ncumul_conf"], 
        #z = df.loc[df['date'] == today3, ['ncumul_conf']], 
        locations = df["canton_full_name"], 
        featureidkey='properties.NAME_1', 
        colorscale = "viridis", 
        colorbar_title = "No. Cases"
        #featureidkey="properties.district",
        #center = {"lat": 46.94809, "lon": 7.44744} 
        ))
    
    fig.update_layout(title_text = 'Confirmed Cases per Canton',
                      title_x=0.5,
                      xaxis_fixedrange = True, # disable zooming/panning, useful for mobile screens
                      yaxis_fixedrange = True, # disable zooming/panning, useful for mobile screens
                      mapbox=dict(style='white-bg',
                                  zoom=6, 
                                  center = {"lat": 46.8181877 , "lon":8.2275124 },
                                  )); 
    
    st.plotly_chart(fig, use_container_width = True)

elif analysis == 'New Cases per Day':
    # display plot options
    selected_cantons, selected_cantons_df, log_y_axis = display_plot_options()
    
    # plot number of new cases per 1000 inhabitants
    plot_covid_time_series(col = "new_cases_per_1000_inhabitants")   
    
    # plot number of new cases
    plot_covid_time_series(col = "new_cases_per_day")
    
    # show raw data if asked
    show_raw_data = st.checkbox('Show raw data', value = False)
    
    if show_raw_data: 
        st.write(df)

elif analysis == 'Cumulative Cases':
    
    # display plot options
    selected_cantons, selected_cantons_df, log_y_axis = display_plot_options()

    # plot cumulative cases per 1000 inhabitants
    plot_covid_time_series(col = "cases_per_1000_inhabitants")   
    
    # plot absolute cumulative cases
    plot_covid_time_series(col = "ncumul_conf")     

    # show raw data if asked
    show_raw_data = st.checkbox('Show raw data', value = False)
    
    if show_raw_data: 
        st.write(df)

# show last update date
today = datetime.date.today()
st.write("Last updated:", today)
# - datetime.timedelta(days=1),


# to be added in the future (possibly)
#time.sleep(60*60*12)  # 12 hours timer
#st_rerun()
    
    
    
    
    
    
    