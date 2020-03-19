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
min_d_cases = 10
min_total_cases = 500
temp_first = data[(data['Status']=='confirmed') & (data['Cases']>min_cases)].groupby(['CountryProvince'])['Date'].min().reset_index().rename(columns={"Date": "FirstDate"})
temp_max = data[(data['Status']=='confirmed') & (data['Cases']>=min_cases)].groupby(['CountryProvince'])['Cases'].max().reset_index().rename(columns={"Cases": "MaxCases"})
temp_first_d = data[(data['Status']=='deaths') & (data['Cases']>min_d_cases)].groupby(['CountryProvince'])['Date'].min().reset_index().rename(columns={"Date": "FirstDateD"})
#adding start date of contagion to data
data = data.set_index('CountryProvince')
data = data.join(temp_first.set_index('CountryProvince'))
data = data.join(temp_max.set_index('CountryProvince'))
data = data.join(temp_first_d.set_index('CountryProvince'))
data["DaysSinceConfirmed"] = np.where(data['Date']>=data['FirstDate'], (data['Date']-data['FirstDate']).dt.days, 0)
data["DaysSinceDeaths"] = np.where(data['Date']>=data['FirstDateD'], (data['Date']-data['FirstDateD']).dt.days, 0)

temp = data[(data["MaxCases"]>=min_total_cases)].copy()
data["DaysSinceDeaths"] = np.where(data['Date']>=data['FirstDateD'], (data['Date']-data['FirstDateD']).dt.days, 0)

def create_confirmed_line_plot(df):
    status = "confirmed"
    
    provinces = df.index.unique()
    plotdata = []

    for province in provinces:
        # What should go inside this Scatter call?
        province_data = df[(df.index == province) & (df["Status"] == status)]
        trace = go.Scatter(x = province_data.DaysSinceConfirmed, 
                        y = province_data.Cases, 
                        mode='lines', 
                        name = province,
                        text = province_data['Date'],
                        hoverinfo = "text+x+name+y"
                        )
        plotdata.append(trace)

    layout = go.Layout(
        title = '(Logarithmic) Daily confirmed cases per Country/Province where more than {} cases have been registered'.format(min_total_cases),
        xaxis = dict(title = 'Day since first {} confirmed local cases'.format(min_cases)), # x-axis label
        yaxis = dict(title = 'Confirmed cases', range=[2,5.5]), # y-axis label
        yaxis_type='log',
        hovermode='closest',
        height=800,
        autosize=True,
        margin=dict(l=50, r=20, b=100, t=100),
        font=dict(family="Courier New, monospace")
    ) 

    fig = dict(data=plotdata, layout=layout)
    return fig

def create_deaths_line_plot(df):
    status = "deaths"
    provinces = df.index.unique()
    plotdata = []

    for province in provinces:
        # What should go inside this Scatter call?
        province_data = df[(df.index == province) & (df["Status"] == status)]
        trace = go.Scatter(x = province_data.DaysSinceDeaths, 
                        y = province_data.Cases, 
                        mode='lines', 
                        name = province,
                        text = province_data['Date'],
                        hoverinfo = "text+x+name+y"
                        )
        plotdata.append(trace)

    layout = go.Layout(
        title = '(Logarithmic) Daily deaths cases per Country/Province where more than {} cases have been registered'.format(min_total_cases),
        xaxis = dict(title = 'Day since first {} confirmed local death cases'.format(min_d_cases)), # x-axis label
        yaxis = dict(title = 'Deaths', range=[1,4]), # y-axis label
        yaxis_type='log',
        hovermode='closest',
        height=800,
        autosize=True,
        margin=dict(l=50, r=20, b=100, t=100),
        font=dict(family="Courier New, monospace")
    ) 

    fig = dict(data=plotdata, layout=layout)
    return fig

fig_confirmed = create_confirmed_line_plot(temp)
fig_deaths = create_deaths_line_plot(temp)

# Create a Dash layout that contains a Graph component:
app.layout = html.Div(
    children=[
    html.Div(
            className="header-title",
            children=[
                html.H2(
                    id="title",
                    children="Coronavirus virus daily updates and comparison",
                ),
            ], style = {"box-shadow": "rgb(240, 240, 240) 5px 5px 5px 0px"},
        ),
    html.Div(children='Virus spread by country and day'),
    html.Div(children='Showing only countries/regions that have reached {} confirmed cases, day zero is set at {} confirmed cases'.format(min_total_cases, min_cases)),
    html.A('Data source', href='https://covid19api.com'),
    html.Div(children='Click to select out a region, double click to go in isolate a region mode'),
    html.Br(),
    dcc.Graph(
        id='log_confirmed',
            figure= fig_confirmed
    ),
    dcc.Graph(id="log_deaths", className="div-card", figure=fig_deaths),
], style = {"font-family": "Courier New, monospace", 'width':1200, 'height':800}
)

# Add the server clause:
if __name__ == '__main__':
    app.run_server()