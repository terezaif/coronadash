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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Launch the application:
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

LOC = "data"
#filename = "{}/daily_json.gzip".format(LOC)
# Create a DataFrame from the .csv file:
#
# data = pd.read_json(filename, compression="gzip")
data = pd.read_json('https://api.covid19api.com/all')

#adding dates and so on
data["Date"] = pd.to_datetime(data["Date"], errors='coerce').dt.date
data["CountryProvince"] = data["Country"]+data["Province"]
#getting start date of contagion
min_cases = 100
temp_first = data[(data['Status']=='confirmed') & (data['Cases']>0)].groupby(['CountryProvince'])['Date'].min().reset_index().rename(columns={"Date": "FirstDate"})
temp_max = data[(data['Status']=='confirmed') & (data['Cases']>=min_cases)].groupby(['CountryProvince'])['Cases'].max().reset_index().rename(columns={"Cases": "MaxCases"})
#adding start date of contagion to data
data = data.set_index('CountryProvince')
data = data.join(temp_first.set_index('CountryProvince'))
data = data.join(temp_max.set_index('CountryProvince'))
data["DaysSinceConfirmed"] = np.where(data['Date']>=data['FirstDate'], (data['Date']-data['FirstDate']).dt.days, 0)

status = "confirmed"
min_total_cases = 500
temp = data[(data["MaxCases"]>=min_total_cases) & (data["Status"] == status)].copy()

provinces = temp.index.unique()
plotdata = []
for province in provinces:
    # What should go inside this Scatter call?
    province_data = temp[temp.index == province]
    trace = go.Scatter(x = province_data.DaysSinceConfirmed, 
                       y = province_data.Cases, 
                       mode='lines', 
                       name = province,
                       text = province_data['Date'],
                       hoverinfo = "text+x+name+y"
                    )
    plotdata.append(trace)

layout_conf = go.Layout(
    title = '(Logarithmic) Daily confirmed cases per Country/Province where more than {} cases have been registered'.format(min_total_cases),
    xaxis = dict(title = 'Day since first {} confirmed local case'.format(min_cases)), # x-axis label
    yaxis = dict(title = 'Confirmed cases'), # y-axis label
    yaxis_type='log',
    hovermode='closest'
) 

# Create a Dash layout that contains a Graph component:
app.layout = html.Div(
    children=[
    html.H1(children='Country/Province comparison '),
    html.Div(children='Virus spread by country and day'),
    html.Div(children='Showing only countries/regions that have reached {} confirmed cases'.format(min_total_cases)),
    html.A('Data source', href='https://covid19api.com'),
    dcc.Graph(
        id='log_confirmed',
            figure={
                'data': plotdata,
                'layout': layout_conf
            }
    )
])

# Add the server clause:
if __name__ == '__main__':
    app.run_server(debug=True)