# %%
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc

# %%
data = pd.read_csv("/Users/tilliedavies/Desktop/DS 4003/data.csv")

# %%
results = pd.read_csv("/Users/tilliedavies/Desktop/DS 4003/Final Project/F1 Data/results.csv")
data2 = pd.merge(results, data[['raceId','driverRef','year','round','driverId']], how='left', on=['driverId','raceId'])
data2 = data2.drop_duplicates()

# %%
data2.dropna(inplace=True)

# %%
data2['round'] = data2['round'].astype(int)

# %%
drivers = pd.read_csv("/Users/tilliedavies/Desktop/DS 4003/Final Project/F1 Data/drivers.csv")

# %%
data['AvgPitStopDuration'] = data.groupby(['raceId', 'driverId'])['pitStopDuration'].transform('mean')
data['AvgPitStopDuration'] = data['AvgPitStopDuration'] / 1000

data2.sort_values(by=['driverRef', 'year', 'round'], inplace=True)
data2['accumulated_points'] = data2.groupby(['driverRef', 'year'])['points'].cumsum()
data2.sort_values(by='round', inplace=True)


# %%
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

app.layout = html.Div([
    html.Div(
        children=[
            html.H1('Formula 1 Dashboard',className="app-header--title"),
            html.Img(src='/Users/tilliedavies/Desktop/DS 4003/Final Project/F1.png', style={'width': '50%', 'height': '50%'})
        ]
    ),
    html.Div(
        children=html.Div([
            html.H5('Interact with the dashboard below to view both driver and Grand Prix overall perfromance from the year 2009 till now.')
        ])
    ),
    html.Div([
        html.H3('Winningest Drivers, by Year'),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in data['year'].unique()],
            value=2023,
            clearable=False,
            style={'width': '100%', 'display': 'inline-block','padding-left': '20px'}),
        dcc.Graph(id='animatedgraph', style={'width': '100%', 'display': 'inline-block','padding-left': '20px'}),
        html.Div(id='table-container')],style={'width': '30%', 'display': 'inline-block','padding-left': '20px'}), 
    html.Div([
        dcc.Dropdown(
            id='grandprix-select',
            options= [{'label': name, 'value': name} for name in data['name'].unique()],
            value='Australian Grand Prix',
            style={'width': '100%', 'display': 'inline-block'}
        ),
        dcc.Graph(id='graph', style={'width': '100%', 'display': 'inline-block'}),
        dcc.Graph(id='hist', style={'width': '100%', 'display': 'inline-block'})
    ],style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        html.H3('Driver Lookup'),
        dcc.Input(id='search-input', type='text', placeholder='Enter last name...',style={'width': '30%', 'display': 'inline-block','padding-left': '20px'}),
        html.Div(id='search-output',style={'width': '100%', 'display': 'inline-block','padding-left': '20px'})
              ],style={'width': '30%', 'display': 'inline-block'})
],style={'vertical-align': 'top'})    

##########################################################
#################APP CALLBACKS############################
##########################################################

@app.callback(
    Output('animatedgraph','figure'),
    [Input('year-dropdown','value')]
)
def updateanimation(selected_year):
    filtered_df2 = data2[data2['year'] == selected_year]
    fig1 = px.bar(filtered_df2, x='accumulated_points',y='driverRef',
            orientation='h',
            animation_frame='round',
            range_x=[0,500], 
            range_y=[0,15], 
            color='driverRef')
    fig1.update_layout(showlegend=False)
    return fig1

@app.callback(
    Output('table-container', 'children'),
    [Input('year-dropdown','value')]
)
def update_table(selected_year):
    filtered_df4 = data2[data2['year'] == selected_year]
    top_10 = filtered_df4.sort_values(by='accumulated_points', ascending=False).head(10)
    table = html.Table([
        html.Thead(html.Tr([
            html.Th('Driver'),
            html.Th('Accumulated Points')
        ])),
        html.Tbody([
            html.Tr([
                html.Td(top_10.iloc[i]['driverRef']),
                html.Td(top_10.iloc[i]['accumulated_points'])
            ]) for i in range(len(top_10))
        ])
    ])
    return table

@app.callback(
    Output('search-output', 'children'),
    [Input('search-input', 'value')]
)
def update_output(last_name):
    if last_name is None:
        return html.Div("Enter a last name to search")
    else:
        search_results = drivers[drivers['surname'].str.lower() == last_name.lower()]
        if search_results.empty:
            return html.Div("No results found")
        else:
            return html.Table([
                html.Thead(html.Tr([html.Th(col) for col in search_results.columns])),
                html.Tbody([
                    html.Tr([
                        html.Td(html.A(search_results.iloc[i][col], href=search_results.iloc[i]['url'])) if col == 'url' else html.Td(search_results.iloc[i][col])
                        for col in search_results.columns
                    ]) for i in range(len(search_results))
                ])
            ])


@app.callback(
    Output('graph', 'figure'),
    [Input('grandprix-select', 'value')]
)
def update_graph(selected_race):
    filtered_df = data[data['name']== selected_race]
    fig = px.scatter(filtered_df, x= 'year',
              y='AvgPitStopDuration',
              color='driverRef',
              title= 'Average Pit Stop Duration per Grand Prix, by driver')
    fig.update_xaxes(title_text='Year')
    fig.update_yaxes(title_text='Avg Pit Stop Duration (milliseconds)')
    return fig

@app.callback(
    Output('hist','figure'),
    [Input('grandprix-select','value')]
)
def update_hist(selected_race):
    filtered_df3 = data[data['name']== selected_race]
    fig2 = px.histogram(filtered_df3, 
                        x='fastestLapSpeed',
                        histfunc='avg',
                        title = 'Distribution of Fastest Lap Speed')
    fig2.update_yaxes(visible=False)
    fig2.update_traces(hoverinfo='skip')
    return fig2

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)



