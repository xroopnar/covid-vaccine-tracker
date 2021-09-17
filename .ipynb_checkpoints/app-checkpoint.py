#from jupyter_dash import JupyterDash  # pip install dash
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import pandas as pd  # pip install pandas
import plotly.express as px
import math
from dash import no_update

from urllib.request import urlopen
import json

############## LOADING APP DATA

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

#state codes
abbr = pd.read_csv("https://raw.githubusercontent.com/xroopnar/DSW2021/main/data/abbr-name.csv",index_col=False,header=None)
abbr.columns = ["state","location"]

#for the county-level state vaccination percentages
us = pd.read_csv("https://raw.githubusercontent.com/xroopnar/DSW2021/main/data/us_vaccine_9month.csv",index_col=0,dtype={"FIPS":str})
#use cdc api 


#for comparing new case count to vaccination percentage in bubble plot over time 
#cases = pd.read_csv("https://raw.githubusercontent.com/xroopnar/DSW2021/main/data/us_9month_covid_cases.csv",index_col=0)
#vacc = pd.read_csv("https://raw.githubusercontent.com/xroopnar/DSW2021/main/data/us_state_vaccinations.csv",index_col=False)
#vacc = vacc.merge(abbr,on="location",how="left")

#worldwide country covid cases
#world = pd.read_csv("https://raw.githubusercontent.com/xroopnar/DSW2021/main/data/WHO%20COVID-19%20global%20table%20data%20September%2011th%202021%20at%205.52.31%20PM.csv",index_col=False)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

############### APP LAYOUT 

#color management
colors = {
    'background': '#6882e8',
    'bodyColor':'#F2DFCE',
    'text': '#ffffff'
}

app.layout = dbc.Container([
    dbc.Row([
    dbc.Col(html.H1("COVID-19 Vaccination Tracker",style={'color': colors['text'],"textAlign":"center"}))
    ],align="center",style={'backgroundColor': colors['background'],"margin-bottom":"10px"}),
    dbc.Row([
             dbc.Col([dcc.Graph(id="ok-map")],width=8),
             dbc.Col([dcc.Graph(id="state-bar")])
    ]),
    dbc.Row([
             dbc.Col([
        dcc.RadioItems(id="pop-radio",
            options=[
                {'label': 'Total Pop', 'value': 'Series_Complete_Pop_Pct'},
                {'label': 'Ages 12+', 'value': 'Series_Complete_12PlusPop_Pct'},
                {'label': 'Ages 65+', 'value': 'Series_Complete_65PlusPop_Pct'}
            ],
            value='Series_Complete_Pop_Pct',
            labelStyle={'display': 'inline-block'},
            style={"width": "80%"}
        ),
#        dcc.Dropdown(
#            id='ok-dropdown',
#            value=us.columns[4],
#            #clearable=False,
#            options=[
#                     {'label': x[1], 'value': x[0]}
#                     for x in {"Series_Complete_Pop_Pct":'% Vaccinated',"Series_Complete_12PlusPop_Pct":'% Vaccinated (12+)',"Series_Complete_18PlusPop_Pct":'% Vaccinated (18+)',"Series_Complete_65PlusPop_Pct":'% Vaccinated (65+)'}.items()
#            ],style={"width": "60%"}),
        dcc.Dropdown(id="ok-date",
            value = us.Date.unique()[0],
            #clearable=False,
            options=[
                    {"label": x,"value": x}
                    for x in us.Date.unique()
            ],style={"width": "60%"}),
        dcc.Dropdown(id="state-map-dropdown",
            value = "OK",
            #clearable=False,
            options=[
                    {"label": x,"value": x}
                    for x in us.Recip_State.sort_values().unique()
            ],style={"width": "60%"}),
    #dcc.Graph(id="ok-map"),
    ],width=8),
    dbc.Col([
#    dcc.Dropdown(
#        id="state-count-dropdown",
#        value=10,
#        options=[
#                 {"label":value,"value":value}
#                 for value in list(range(1,21))
#                ]
#        ),
    dcc.Slider(id="count-slider",
               min=5,
               max=20,
               marks = {x:str(x) for x in list(range(1,21))},
               value=5
    )
    #dcc.Graph(id="state-bar")
    ])
    ]),
])

@app.callback(Output('ok-map', 'figure'),
              #Input('ok-dropdown', 'value'),
              Input('pop-radio', 'value'),
              Input("ok-date","value"),
              Input("state-map-dropdown","value"))
def update_us_map(value,date,state):

  fig = px.choropleth(us[(us.Date==date) & (us.Recip_State==state)], geojson=counties, locations='FIPS', color=value,
                           color_continuous_scale="sunset",
                           range_color=(0, 80),
                           scope="usa",
                           labels={"Series_Complete_Pop_Pct":'%',"Series_Complete_12PlusPop_Pct":'%',"Series_Complete_18PlusPop_Pct":'%',"Series_Complete_65PlusPop_Pct":'%',"Recip_County":"County","Recip_State":"State"},
                           hover_data={"FIPS":False,"Recip_County":True,"Recip_State":False},
                           #use fitbounds when looking at a singular state instead of entire USA
                           #otherwise exclude fitbounds
                           fitbounds="locations",
                           title="Hello world"
                          )

  fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},transition_duration=500)

  return(fig)

@app.callback(Output("state-bar","figure"),
              Input("state-map-dropdown","value"),             
              #Input("state-time-dropdown","value"),
              Input("count-slider","value"))
              #Input("state-count-dropdown","value"))
def update_state_time(value,n):
  #n=10
  #print("n:",n)
  df = us[us.Recip_State==value].sort_values(by="Date",ascending=True)
  df = df[df.Recip_County.isin(df.Recip_County.unique()[0:n])]
  fig = px.line(df,x="Date",y="Series_Complete_Pop_Pct",line_group="Recip_County",color="Recip_County")
  fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},transition_duration=500)
  return(fig)


ADDRESS = "10.84.146.29"
PORT = 8030
app.run_server(debug=True, host=ADDRESS, port=PORT)
