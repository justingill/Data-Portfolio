'''
Project: Fitness Web Tracker
Author: Justin Gill
Last Updated: 2/14/2019
Description: This project uses the dash framework to implement
a fitness tracker which tracks exercises, reps, and sets. It
can then be plotted to a graph and displayed to the website.
'''

#Import necessary libraries
import dash
import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import plotly.graph_objs as go
import datetime as dt
import pandas as pd
import numpy as np
import csv

# We want this to be switched to a SQL database at some point.
# Currently we read from a csv file that can be created with the columns
# Exercise, Reps, Sets, and Datetime
df = pd.read_csv('workout.csv',parse_dates=['Datetime'])

# This function get_data() reads a csv file. It is used to update our
# data when we submit a new entry.
def get_data():
    data = pd.read_csv('workout.csv', parse_dates=['Datetime'])
    data.sort_values('Datetime',inplace=True)
    return data

# Style sheet to change layout of web page.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Create our dash application
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Build the layout of the website
app.layout = html.Div(children=[

    # A centered header
    html.H1(
        children="Workout Application",
        style={
            'textAlign':'center'
        }
    ),

    # 3 input boxes with a submit button at the end.
    html.Div(children=[
        dcc.Input(id='Exercise', value='', type='text'),
        dcc.Input(id='Weight', value='', type='text'),
        dcc.Input(id='Rep', value='', type='text'),
        html.Button('Submit', id='button'),
    ]),

    # Outputs whatever is submitted with the submit button.
    html.Div(id='output-container-button'),

    html.Br(),

    # A dynamic dropdown used to display the various exercises.
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': i, 'value': i} for i in list(df['Exercise'].value_counts().index)
        ],
    ),

    html.Br(),

    html.Div(id='output-container2'),

    # A line graph
    dcc.Graph(
        id='graph1'
    ),

    html.Br(),

    # A single date picker to pick a specific date.
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        clearable=True,
        min_date_allowed=min(df['Datetime']),
        max_date_allowed=max(df['Datetime']),
        initial_visible_month=max(df['Datetime']),
        date=max(df['Datetime'])
    ),

    # Displays a data table with our updated csv file.
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data = df[df['Datetime'] == max(df['Datetime'])].to_dict("rows")
    )
])

#This callback is used to update our table with the current date picked.
@app.callback(
    Output('table','data'),
    [Input('my-date-picker-single','date')]
)
def output_workouts(date):
    data = get_data()
    return data[data['Datetime'] == date].to_dict("rows")

# This callback takes in the input from the three boxes and saves them
# to a csv file when the submit button is pressed.
@app.callback(
    Output('output-container-button', 'children'),
    [Input('button','n_clicks')],
    [State('Exercise', 'value'),
     State('Weight', 'value'),
     State('Rep', 'value')]
)
def update_output(nclicks,exercise,weight,rep):
    if rep == '' or exercise == '' or weight == '':
        return ''
    else:
        temp = dt.date.today()

        #pd.concat([pd.DataFrame([[exercise,weight,rep,temp]], columns=df.columns), df]).reset_index(drop=True)

        with open('workout.csv', mode='w',newline="") as file:
            writer = csv.writer(file,delimiter=',')
            writer.writerow(list(df.columns))
            for rows in range(len(df)):
                writer.writerow(list(df.iloc[rows]))
            writer.writerow([exercise,weight,rep,temp])

        return 'Saved - Performed {} at {} for {} on {}.'.format(exercise,
                                                                     weight,
                                                                     rep,

                                                                     temp.strftime('%m/%d/%Y'))

# This callback will update the dropdown menu to our most current data/
@app.callback(
    Output('dropdown', 'options'),
    [Input('output-container-button','children')]
)
def update_drop(nclicks):
    data = get_data()
    return [{'label': vals, 'value': vals} for vals in list(data['Exercise'].value_counts().index)]

# This callback will plot a line graph based on the chose dropdown option.
@app.callback(
    Output('graph1', 'figure'),
    [Input('dropdown','value')]
)
def update_figure(value):
    data = get_data()
    fig = {
        'data': [{
            'y': data[data['Exercise'] == value]['Weight'],
            'x': data[data['Exercise'] == value]['Datetime'].apply(lambda x: x.strftime('%m/%d/%Y %H:%M')),
            'text':['{} x {}'.format(weight,rep)
                    for (weight,rep)
                    in zip(data[data['Exercise'] == value]['Weight'],
                           data[data['Exercise'] == value]['Rep'])],

            'hoverinfo':'text',
            'mode': 'lines+markers',
            'marker':{'size':10,
                      'line':{'width':4}}
        }],
        'layout':{
            'title': ('Line Plot of {} by Weight over Time'.format(value)),
            'xaxis': {
                'title': 'Date'
            },
            'yaxis': {
                'title': 'Weight (lbs)'
            }
        }
    }

    return fig

if __name__ == '__main__':
    # Run our server.
    app.run_server(debug=True)