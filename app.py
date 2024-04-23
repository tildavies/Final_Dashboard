# %%
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# %%
data = pd.read_csv("data.csv")
drivers = pd.read_csv("drivers.csv")
results = pd.read_csv("results.csv")

# %%
data2 = pd.merge(results, data[['raceId','driverRef','year','round','driverId']], how='left', on=['driverId','raceId'])
data2 = data2.drop_duplicates()
data2.dropna(inplace=True)
data2['round'] = data2['round'].astype(int)

# %%
data['AvgPitStopDuration'] = data.groupby(['raceId', 'driverId'])['pitStopDuration'].transform('mean')
data['AvgPitStopDuration'] = data['AvgPitStopDuration'] / 1000
data2.sort_values(by=['driverRef', 'year', 'round'], inplace=True)
data2['accumulated_points'] = data2.groupby(['driverRef', 'year'])['points'].cumsum()
data2.sort_values(by='round', inplace=True)

# %%
image_paths = {
    'Abu Dhabi Grand Prix': 'abudhabi.png',
    'Austrian Grand Prix': 'austrain.png',
    'Azerbaijan Grand Prix': 'azerbaijan.png',
    'Bahrain Grand Prix': 'bahrain.png',
    'Belgian Grand Prix':'belgian.png',
    'Brazilian Grand Prix':'brazilian.png',
    'British Grand Prix':'british.png',
    'Canadian Grand Prix':'canadian.png',
    'Chinese Grand Prix':'chinese.png',
    'Dutch Grand Prix':'dutch.png',
    'Hungarian Grand Prix':'hungarian.png',
    'Italian Grand Prix':'italian.png',
    'Japanese Grand Prix':'japanese.png',
    'Mexican Grand Prix':'mexican.png',
    'Miami Grand Prix':'miami.png',
    'Monaco Grand Prix':'monaco.png',
    'Qatar Grand Prix':'qatar.png',
    'Saudi Arabian Grand Prix':'saudiaraibian.png',
    'Singapore Grand Prix':'singapore.png',
    'Spanish Grand Prix':'spanish.png',
    'United States Grand Prix':'us.png'
}

# %%
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

app.layout = html.Div([
    html.Div(
        children=[
            html.H1('Formula 1 Dashboard',className="app-header--title")
        ]
    ),
    html.Div(
        children=html.Div([
            html.H5('Interact with the dashboard below to view both driver and Grand Prix overall perfromance from the year 2009 till now.')
        ])
    ),
    html.Div([
        html.H4('Winningest Drivers, by Year'),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in data['year'].unique()],
            value=2023,
            clearable=False,
            style={'width': '100%', 'display': 'inline-block','padding-left': '20px'}),
        dcc.Graph(id='animatedgraph', style={'width': '100%', 'display': 'inline-block','padding-left': '20px','vertical-align': 'top'}),
        html.Div(id='table-container',style={'padding-top': '20px', 'padding-left': '20px'})],style={'width': '30%', 'display': 'inline-block','padding-left': '20px','vertical-align': 'top','padding-top': '20px'}), 
    html.Div([
        html.H3('Grand Prix Maps'),
        dcc.Dropdown(
            id='image-dropdown',
            options=[{'label': option, 'value': option} for option in image_paths.keys()],
            value='Australian Grand Prix'),
        html.Img(id='image-display'),
        html.H4('Comparing Grand Prix Pit Stops'),
        dcc.Dropdown(
            id='grandprix-select',
            options= [{'label': name, 'value': name} for name in data['name'].unique()],
            value='Australian Grand Prix',
            style={'width': '100%', 'display': 'inline-block'}),
        dcc.Graph(id='graph', style={'width': '100%', 'display': 'inline-block'}),
        html.H4('Distribution of Lap Speeds', style={'padding-top':'40px'}),
        dcc.Graph(id='hist', style={'width': '100%', 'display': 'inline-block'})],style={'width': '30%', 'display': 'inline-block','vertical-align': 'top','padding-top': '20px'}),
    html.Div([
        html.Img(src='/Users/tilliedavies/Desktop/DS 4003/Final Project/F1.png', style={'width': '50%', 'height': '50%','vertical-align': 'top'}),
        html.H4('Driver Lookup'),
        dcc.Input(id='search-input', type='text', placeholder='Enter last name...',style={'width': '30%', 'display': 'inline-block','padding-left': '20px','padding-top': '20px'}),
        html.Div(id='search-output',style={'width': '100%', 'display': 'inline-block','padding-left': '20px'}),
        html.H4('Driver Nationalities',style={'padding-top':'40px'}),
        dcc.Graph(id='world-map',style={'width': '100%', 'display': 'inline-block','padding-left': '20px'})
              ],style={'width': '30%', 'display': 'inline-block','vertical-align': 'top','padding-left': '20px', 'padding-top': '20px'})
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
    sorted_df = filtered_df2.sort_values(by='accumulated_points', ascending=True)
    
    fig1 = px.bar(sorted_df, 
                  x='accumulated_points', 
                  y='driverRef',
                  orientation='h',
                  animation_frame='round',
                  range_x=[0, 400], 
                  range_y=[0, 20],
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
    Output('image-display', 'src'),
    [Input('image-dropdown', 'value')]
)
def update_image(option):
    return image_paths.get(option, 'default.jpg') 



@app.callback(
    Output('graph', 'figure'),
    [Input('grandprix-select', 'value')]
)
def update_graph(selected_race):
    filtered_df = data[data['name']== selected_race]
    fig = px.scatter(filtered_df, x= 'year',
              y='AvgPitStopDuration',
              color='driverRef')
    fig.update_xaxes(title_text='Year')
    fig.update_yaxes(title_text='Avg Pit Stop Duration (milliseconds)')
    fig.update_layout(showlegend=False)
    return fig

@app.callback(
    Output('hist','figure'),
    [Input('grandprix-select','value')]
)
def update_hist(selected_race):
    filtered_df3 = data[data['name']== selected_race]
    fig2 = px.histogram(filtered_df3, 
                        x='fastestLapSpeed',
                        histfunc='avg')
    fig2.update_yaxes(visible=False)
    fig2.update_xaxes(title_text='Fastest Lap Speed (km/hr)')
    fig2.update_traces(hoverinfo='skip')
    return fig2

@app.callback(
    Output('world-map', 'figure'),
    [Input('world-map', 'clickData')]
)
def update_map(click_data):
    # Group data by nationality and count the number of drivers
    nationality_counts = drivers['nationality'].value_counts().reset_index()
    nationality_counts.columns = ['nationality', 'Count']
    
    # Create choropleth map with Plotly
    fig7 = go.Figure(go.Choropleth(
        locations=nationality_counts['nationality'],
        z=nationality_counts['Count'],
        locationmode='country names',
        colorscale='Reds',
        colorbar_title='Driver Count',
        zmin=0,
        zmax=50
    ))

    fig7.update_layout(
        geo=dict(
            showcoastlines=True,
        ),
        mapbox_style="carto-positron"
    )

    return fig7


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)



