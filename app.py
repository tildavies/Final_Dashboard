# %%
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# %%
data = pd.read_csv("data/data.csv")
drivers = pd.read_csv("data/drivers.csv")
results = pd.read_csv("data/results.csv")

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
    'Abu Dhabi Grand Prix': 'https://cdn.racingnews365.com/Circuits/Abu-Dhabi/_503xAUTO_crop_center-center_none/f1_2024_abu_outline.png?v=1708705548',
    'Australian Grand Prix': 'https://cdn.racingnews365.com/Circuits/Australia/_503xAUTO_crop_center-center_none/f1_2024_aus_outline.png?v=1708703549',
    'Austrian Grand Prix': 'https://cdn.racingnews365.com/Circuits/Austria/_503xAUTO_crop_center-center_none/f1_2024_aut_outline.png?v=1708704458',
    'Azerbaijan Grand Prix': 'https://cdn.racingnews365.com/Circuits/Azerbaijan/_503xAUTO_crop_center-center_none/f1_2024_aze_outline.png?v=1708704459',
    'Bahrain Grand Prix': 'https://cdn.racingnews365.com/Circuits/Bahrain/_503xAUTO_crop_center-center_none/f1_2024_bhr_outline.png?v=1708703548',
    'Belgian Grand Prix':'https://cdn.racingnews365.com/Circuits/Belgium/_503xAUTO_crop_center-center_none/f1_2024_bel_outline.png?v=1708704458',
    'Brazilian Grand Prix':'https://cdn.racingnews365.com/Circuits/Brazil/_503xAUTO_crop_center-center_none/f1_2024_bra_outline.png?v=1708705480',
    'British Grand Prix':'https://cdn.racingnews365.com/Circuits/Great-Britain/_503xAUTO_crop_center-center_none/f1_2024_gbr_outline.png?v=1708704458',
    'Canadian Grand Prix':'https://cdn.racingnews365.com/Circuits/Canada/_503xAUTO_crop_center-center_none/f1_2024_can_outline.png?v=1708704457',
    'Chinese Grand Prix':'https://cdn.racingnews365.com/Circuits/China/_503xAUTO_crop_center-center_none/f1_2024_chn_outline.png?v=1708703688',
    'Dutch Grand Prix':'https://cdn.racingnews365.com/Circuits/The-Netherlands/_503xAUTO_crop_center-center_none/f1_2024_nld_outline.png?v=1708704459',
    'Hungarian Grand Prix':'https://cdn.racingnews365.com/Circuits/Hungary/_503xAUTO_crop_center-center_none/f1_2024_hun_outline.png?v=1708704458',
    'Italian Grand Prix':'https://cdn.racingnews365.com/Circuits/Italy/_503xAUTO_crop_center-center_none/f1_2024_ita_outline.png?v=1708704459',
    'Japanese Grand Prix':'https://cdn.racingnews365.com/Circuits/Japan/_503xAUTO_crop_center-center_none/f1_2024_jap_outline.png?v=1708703688',
    'Mexican Grand Prix':'https://cdn.racingnews365.com/Circuits/Mexico/_503xAUTO_crop_center-center_none/f1_2024_mex_outline.png?v=1708704579',
    'Miami Grand Prix':'https://cdn.racingnews365.com/Circuits/Miami/_503xAUTO_crop_center-center_none/f1_2024_mia_outline.png?v=1708703688',
    'Monaco Grand Prix':'https://cdn.racingnews365.com/Circuits/Monaco/_503xAUTO_crop_center-center_none/f1_2024_mco_outline.png?v=1708704457',
    'Qatar Grand Prix':'https://cdn.racingnews365.com/Circuits/Qatar/_503xAUTO_crop_center-center_none/f1_2024_qat_outline.png?v=1708705481',
    'Saudi Arabian Grand Prix':'https://cdn.racingnews365.com/Circuits/Saudi-Arabia/_503xAUTO_crop_center-center_none/f1_2024_sau_outline.png?v=1708703549',
    'Singapore Grand Prix':'https://cdn.racingnews365.com/Circuits/Singapore/_503xAUTO_crop_center-center_none/f1_2024_sgp_outline.png?v=1708704459',
    'Spanish Grand Prix':'https://cdn.racingnews365.com/Circuits/Spain/_503xAUTO_crop_center-center_none/f1_2024_spn_outline.png?v=1708704458',
    'United States Grand Prix':'https://cdn.racingnews365.com/Circuits/United-States/_503xAUTO_crop_center-center_none/f1_2024_usa_outline.png?v=1708704579'
}

# %%
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

app.layout = html.Div([
    html.Div(
        children=[
            html.H1('Formula 1 Dashboard',className="app-header--title", style={'padding-top':'40px'})
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
        html.Img(id='image-display',style={'width': '50%', 'height': 'auto'} ),
        html.H4('Comparing Grand Prix Pit Stops'),
        dcc.Dropdown(
            id='grandprix-select',
            options= [{'label': name, 'value': name} for name in data['name'].unique()],
            value='Australian Grand Prix',
            style={'width': '100%', 'display': 'inline-block'}),
        dcc.Graph(id='graph', style={'width': '100%', 'display': 'inline-block'}),
        html.H4('Distribution of Lap Speeds', style={'padding-top':'40px'}),
        dcc.Graph(id='hist', style={'width': '100%', 'display': 'inline-block'})],style={'width': '30%', 'display': 'inline-block','vertical-align': 'top','padding-top': '20px', 'padding-left':'38px'}),
    html.Div([
        html.Img(src='https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1280px-F1.svg.png', style={'width': '50%', 'height': '50%','vertical-align': 'top'}),
        html.H4('Driver Lookup'),
        dcc.Input(id='search-input', type='text', placeholder='Enter last name...',style={'width': '30%', 'display': 'inline-block','padding-left': '20px','padding-top': '20px'}),
        html.Div(id='search-output',style={'width': '100%', 'display': 'inline-block','padding-left': '20px'}),
        html.H4('Driver Nationalities',style={'padding-top':'40px'}),
        dcc.Graph(id='world-map',style={'width': '100%', 'display': 'inline-block','padding-left': '20px'}),
        html.Div(style={'position': 'absolute', 'top': '10px', 'right': '10px'}, children=[
            html.A(html.Button('GitHub', style={'margin-right': '10px'}), href='https://github.com/tildavies/Final_Dashboard/', target='_blank')])])
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



