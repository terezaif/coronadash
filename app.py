#######
# Objective: build a dashboard that imports OldFaithful.csv
# from the data directory, and displays a scatterplot.
# The field names are:
# 'D' = date of recordings in month (in August),
# 'X' = duration of the current eruption in minutes (to nearest 0.1 minute),
# 'Y' = waiting time until the next eruption in minutes (to nearest minute).
######

# Perform imports here:
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# Launch the application:
app = dash.Dash()

LOC = "data"
#filename = "{}/daily_json.gzip".format(LOC)
# Create a DataFrame from the .csv file:
#
# data = pd.read_json(filename, compression="gzip")
data = pd.read_json('https://api.covid19api.com/all')

#adding dates and so on
data["Date"] = pd.to_datetime(data["Date"], errors='coerce').dt.date
data["CountryProvince"] = data["Country"]+data["Province"]
temp = data[(data['Status']=='confirmed') & (data['Cases']>0)].groupby(['CountryProvince'])['Date'].min().reset_index().rename(columns={"Date": "FirstDate"})
#adding start date of contagion to data
data = data.set_index('CountryProvince').join(temp.set_index('CountryProvince'))
data["DaysSinceConfirmed"] = np.where(data['Date']>=data['FirstDate'], (data['Date']-data['FirstDate']).dt.days, 0)
temp_max = data[(data['Status']=='confirmed') & (data['Cases']>=0)].groupby(['CountryProvince'])['Cases'].max().reset_index()

status = "confirmed"
provinces = data.index.unique()
plotdata_conf = []
for province in provinces:
    if (temp_max.loc[temp_max["CountryProvince"]==province]["Cases"].values[0] >=500):
    # What should go inside this Scatter call?
        province_data = data[(data.index == province) & (data["Status"] == status)]
        trace = go.Scatter(x = province_data.DaysSinceConfirmed, 
                           y = province_data.Cases, 
                           mode='lines', 
                           name = province,
                           text = data['Date'],
                           hoverinfo = "text+x+name+y"
                          )
        plotdata_conf.append(trace)

layout_conf = go.Layout(
    title = '(Logarithmic) Daily confirmed cases per Country/Province where more than 1000 cases have been registered',
    xaxis = dict(title = 'Day since first confirmed local case'), # x-axis label
    yaxis = dict(title = 'Confirmed cases'), # y-axis label
    yaxis_type='log',
    hovermode='closest'
) 

# Create a Dash layout that contains a Graph component:
app.layout = html.Div([
    html.H1(children='Country/Province comparison '),
    html.Div(children='Virus spread by country and day'),
    html.Div(children='Showing only countries/regions that have reached 500 confirmed cases'),
    html.Div([
        dcc.Graph(
            id='log_confirmed',
            figure={
                'data': plotdata_conf,
                'layout': layout_conf
            }
        )
    ],style={'paddingTop':35})
   
])

# Add the server clause:
if __name__ == '__main__':
    app.run_server()