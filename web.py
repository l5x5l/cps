import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import random
import pymysql
import plotly.graph_objs as go 
import thread
import threading

X = []
Y = []
lock = threading.Lock()

for i in range(8):
    X.append([])
    Y.append([])

th = threading.Thread(target=thread.monitoring, args=(Y,X, lock))
th.start()

def furnace(furnace_number):
    class_name = 'furnace' + str(furnace_number)
    
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(class_name, className=class_name),
                html.P('this is furnace' + str(furnace_number)),
                dcc.Link(dbc.Button("Go furnace" + str(furnace_number), color='primary', id = ('furnace_button' + str(furnace_number))), href='./furnace' + str(furnace_number)),
            ]
        )
    )

def main_page():
    return html.Div(
        [
            dbc.Row([
                dbc.Col(furnace(1), width=3),
                dbc.Col(furnace(2), width=3),
                dbc.Col(furnace(3), width=3),
                dbc.Col(furnace(4), width=3)
            ],
            no_gutters=True),  
            dbc.Row([
                dbc.Col(furnace(5), width=3),
                dbc.Col(furnace(6), width=3),
                dbc.Col(furnace(7), width=3),
                dbc.Col(furnace(8), width=3)
            ],
            no_gutters=True)
        ]
    )

def furnace_page(furnace_number):
    return html.Div([
        dbc.Row([]),
        dcc.Link(dbc.Button("Go main", color='primary', id = ('goto_main_button' + str(furnace_number))), href='./'),
        dbc.Row([
            html.Div([
                dcc.Graph(id = 'live-temp1' + str(furnace_number), animate=False),
            ], style={'width':'22%'}), 
            html.Div([
                dcc.Graph(id = 'live-temp2' + str(furnace_number), animate=False),
            ], style={'width':'22%'}),
            html.Div([
                dcc.Graph(id = 'live-temp3' + str(furnace_number), animate=False),
            ], style={'width':'22%'}), 
            html.Div([
                dcc.Graph(id = 'live-temp4' + str(furnace_number), animate=False),
            ], style={'width':'22%'})               
        ]),
        dbc.Row([
            html.Div([
                dcc.Graph(id = 'live-temp5' + str(furnace_number), animate=False),
            ], style={'width':'22%'}), 
            html.Div([
                dcc.Graph(id = 'live-temp6' + str(furnace_number), animate=False),
            ], style={'width':'22%'}),
            html.Div([
                dcc.Graph(id = 'live-flow' + str(furnace_number), animate=False),
            ], style={'width':'22%'}), 
            html.Div([
                dcc.Graph(id = 'live-press' + str(furnace_number), animate=False),
            ], style={'width':'22%'})           
        ])
    ])

main_page = main_page()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Location(id = 'url', refresh=False),
    html.P(id='placeholder'),
    dcc.Interval(id = 'graph-update', interval=1000, n_intervals=0),
    html.Div(id='page_content')
])

#callback 함수 8개 생성
def update_graph(n, url):
    try:
        i = int(url[-1])
    except:
        raise PreventUpdate
    i = i - 1
    times = X[i]
    temp1, temp2, temp3, temp4, temp5, temp6, flow, press = [], [], [], [], [], [], [], []
    for value in Y[i]:
        temp1.append(value[1])
        temp2.append(value[2])
        temp3.append(value[3])
        temp4.append(value[4])
        temp5.append(value[5])
        temp6.append(value[6])
        flow.append(value[7])
        press.append(value[8])

    #ymin = 0 if len(values) == 0 else min(values)
    #ymax = 30 if len(values) == 0 else max(values)
    ymin = 0
    ymax = 1000
    xmin = 0 if len(times) == 0 else min(times)
    xmax = 30 if len(times) == 0 else max(times)

    temp1 = go.Scatter(
        x = times,
        y = temp1,
        name = 'Scatter',
        mode = 'lines+markers'
    )
    temp2 = go.Scatter(
        x = times,
        y = temp2,
        name = 'Scatter',
        mode = 'lines+markers'
    )
    temp3 = go.Scatter(
        x = times,
        y = temp3,
        name = 'Scatter',
        mode = 'lines+markers'
    )
    temp4 = go.Scatter(
        x = times,
        y = temp4,
        name = 'Scatter',
        mode = 'lines+markers'
    )
    temp5 = go.Scatter(
        x = times,
        y = temp5,
        name = 'Scatter',
        mode = 'lines+markers'
    )
    temp6 = go.Scatter(
        x = times,
        y = temp6,
        name = 'Scatter',
        mode = 'lines+markers'
    )
    flow = go.Scatter(
        x = times,
        y = flow,
        name = 'Scatter',
        mode = 'lines+markers'
    )
    press = go.Scatter(
        x = times,
        y = press,
        name = 'Scatter',
        mode = 'lines+markers'
    )
    return {'data': [temp1], 'layout' : go.Layout(xaxis=dict(range=[xmin,xmax]),yaxis = dict(range = [ymin,ymax]),)}, \
        {'data': [temp2], 'layout' : go.Layout(xaxis=dict(range=[xmin,xmax]),yaxis = dict(range = [ymin,ymax]),)} , \
        {'data': [temp3], 'layout' : go.Layout(xaxis=dict(range=[xmin,xmax]),yaxis = dict(range = [ymin,ymax]),)} , \
        {'data': [temp4], 'layout' : go.Layout(xaxis=dict(range=[xmin,xmax]),yaxis = dict(range = [ymin,ymax]),)} , \
        {'data': [temp5], 'layout' : go.Layout(xaxis=dict(range=[xmin,xmax]),yaxis = dict(range = [ymin,ymax]),)} , \
        {'data': [temp6], 'layout' : go.Layout(xaxis=dict(range=[xmin,xmax]),yaxis = dict(range = [ymin,ymax]),)} , \
        {'data': [flow], 'layout' : go.Layout(xaxis=dict(range=[xmin,xmax]),yaxis = dict(range = [0,100]),)} , \
        {'data': [press], 'layout' : go.Layout(xaxis=dict(range=[xmin,xmax]),yaxis = dict(range = [0,100]),)} 


for i in range(8):
    app.callback(
        Output('live-temp1' + str(i + 1), 'figure'),
        Output('live-temp2' + str(i + 1), 'figure'),
        Output('live-temp3' + str(i + 1), 'figure'),
        Output('live-temp4' + str(i + 1), 'figure'),
        Output('live-temp5' + str(i + 1), 'figure'),
        Output('live-temp6' + str(i + 1), 'figure'),
        Output('live-flow' + str(i + 1), 'figure'),
        Output('live-press' + str(i + 1), 'figure'),
        Input('graph-update', 'n_intervals'),
        State('url', 'pathname')
    )(update_graph)


@app.callback(Output('page_content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/furnace1':
        return furnace_page(1)
    elif pathname == '/furnace2':
        return furnace_page(2)
    elif pathname == '/furnace3':
        return furnace_page(3)
    elif pathname == '/furnace4':
        return furnace_page(4)
    elif pathname == '/furnace5':
        return furnace_page(5)
    elif pathname == '/furnace6':
        return furnace_page(6)
    elif pathname == '/furnace7':
        return furnace_page(7)
    elif pathname == '/furnace8':
        return furnace_page(8)
    else:
        return main_page

if __name__ == '__main__':
    app.run_server(host = '165.246.44.133')
