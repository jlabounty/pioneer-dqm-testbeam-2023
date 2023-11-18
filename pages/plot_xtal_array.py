from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.subplots
import plotly.graph_objects as go
import plotly
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import dash
import hist
import jsonpickle
import analysis.helpers as helpers
import dash_bootstrap_components as dbc

# app = Dash(__name__)
dash.register_page(__name__)

layout = html.Div([
    html.H4('Plot an array of traces'),
    
    html.Div([
        dbc.Row([
            dbc.Col([dcc.Graph(id="lyso-hist-array", style={'display': 'inline-block'}),], width='auto'),
            dbc.Col([dcc.Graph(id="trace-array", style={'display': 'inline-block'}),], width='auto'),

        ]),
        dbc.Row(
            dbc.Col([dcc.Graph(id="lyso-trace-list-layout", style={'display': 'inline-block'}),], width='full')
        ),
        dbc.Row([
            dbc.Col([dcc.Graph(id="nai-array", style={'display': 'inline-block'}),], width='auto'),
            dbc.Col([dcc.Graph(id="hodo-array" , style={'display': 'inline-block'}),], width='auto'),
            dbc.Col([dcc.Graph(id="hodo-hist", style={'display': 'inline-block'}),], width='auto'),
        ]),
    ]),
])

@callback(
    Output("lyso-trace-list-layout", "figure"), 
    Input('traces', 'data'),
    Input('lyso-trace-x-limit-low', 'value'),
    Input('lyso-trace-x-limit-high', 'value'),
    Input('lyso-trace-y-limit-low', 'value'),
    Input('lyso-trace-y-limit-high', 'value'),
    Input('lyso-trace-options', 'value'),
)
def update_trace_list_layout(data, xlow, xhigh, ylow, yhigh, options):
    fig = plotly.subplots.make_subplots(
        cols=5, rows=2,
        shared_xaxes='all',
        shared_yaxes='all',
    )

    for i in range(data['n_lyso']):
        samples_x = list(range(len(data['traces_lyso'][i])))
        fig.add_trace(go.Scatter(
            x=samples_x, 
            y=data['traces_lyso'][i],
            name = f'LYSO {i}'
            ), 
                    #   title=f'X{i}',
            col=i % 5 + 1,
            row=i//5 + 1 
        )
        # break


    if( 1 not in options ):
        fig.update_xaxes(range=[xlow,xhigh])   
    else:
        fig.update_xaxes(autorange=True)
    if( 3 not in options ):
        fig.update_yaxes(range=[ylow,yhigh])
    else:
        fig.update_yaxes(autorange=True)

    fig.update_layout(
        # autosize=True,
        height=700, width=1800
    )
    return fig



@callback(
    Output("trace-array", "figure"), 
    Input('traces', 'data'),
    Input('lyso-trace-x-limit-low', 'value'),
    Input('lyso-trace-x-limit-high', 'value'),
    Input('lyso-trace-y-limit-low', 'value'),
    Input('lyso-trace-y-limit-high', 'value'),
    Input('lyso-trace-options', 'value'),
)
def update_graph(data, xlow, xhigh, ylow, yhigh, options):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    fig = plotly.subplots.make_subplots(
        rows=6, cols=8,
        shared_xaxes='all',
        shared_yaxes='all',
        specs=[
            [None,{'colspan': 2, 'rowspan':2},None, {'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2}, None,None],
            [None,]*8,
            [{'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2},None],
            [None,]*8,
            [None,{'colspan': 2, 'rowspan':2},None, {'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2}, None,None],
            [None,]*8,
        ],
        vertical_spacing=0.075,
        horizontal_spacing=0.08
    )

    this_map = {
         0:[1,2],
         1:[1,4],
         2:[1,6],
         3:[3,1],
         4:[3,3],
         5:[3,5],
         6:[3,7],
         7:[5,2],
         8:[5,4],
         9:[5,6],
    }

    for i in range(10):
        samples = list(range(len(data['traces_lyso'][i])))
        fig.add_trace(
            go.Scatter(
                x=samples, 
                y=data['traces_lyso'][i], 
                name=f'LYSO {i}'
            ), 
            row=this_map[i][0],
            col=this_map[i][1] 
        )

    if( 1 not in options ):
        fig.update_xaxes(range=[xlow,xhigh])   
    else:
        # fig.update_xaxes(autorange=True)
        fig.update_xaxes(matches='x1')
        # pass
    if( 3 not in options ):
        fig.update_yaxes(range=[ylow,yhigh])
    else:
        fig.update_yaxes(matches='y1')
        # fig.update_layout(
        #     shared_yaxes='all',
        # )
        # pass

    return fig

@callback(
    Output("lyso-hist-array", "figure"), 
    Input('histograms', 'data')
)
def update_lyso_hist_array(input):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    hists = jsonpickle.decode(input)
    fig = plotly.subplots.make_subplots(
        rows=6, cols=8,
        # specs = [[{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 2, 'rowspan':2},None]]*3,
        specs=[
            [None,{'colspan': 2, 'rowspan':2},None, {'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2}, None,None],
            [None,]*8,
            [{'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2},None],
            [None,]*8,
            [None,{'colspan': 2, 'rowspan':2},None, {'colspan': 2, 'rowspan':2},None,{'colspan': 2, 'rowspan':2}, None,None],
            [None,]*8,
            # [None,{'colspan': 2, 'rowspan':2},{'colspan': 2, 'rowspan':2},{'colspan': 2, 'rowspan':2}, None],
        ],
        shared_xaxes='all',
        shared_yaxes='all',
        # print_grid=True,
        vertical_spacing=0.075,
        horizontal_spacing=0.08
    )

    this_map = {
         0:[1,2],
         1:[1,4],
         2:[1,6],
         3:[3,1],
         4:[3,3],
         5:[3,5],
         6:[3,7],
         7:[5,2],
         8:[5,4],
         9:[5,6],
    }

    for i in range(10):
        # samples = list(range(len(data['traces_lyso'][i])))
        # fig.add_trace(go.Scatter(x=samples, y=data['traces_lyso'][i], name=f'LYSO {i}'), row=this_map[i][0],col=this_map[i][1] )
        fig.add_trace(
            # go.Scatter(
            #     x=samples, 
            #     y=data['traces_lyso'][i], 
            #     name=f'LYSO {i}'
            # ), 
            helpers.hist_to_plotly_bar(hists[f'lyso_{i}'],name=f'LYSO {i}'),
            row=this_map[i][0],
            col=this_map[i][1] 
        )
    fig.update_yaxes(type="log")
    fig.update_xaxes(range=[0,100_000])
    return fig



@callback(
    Output("hodo-array", "figure"), 
    Input('traces', 'data')
)
def update_hodo(data):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    fig = plotly.subplots.make_subplots(
        rows=6, cols=6,
        specs = [
            [None, {'colspan': 5, 'rowspan':1}] + [None,]*4,
            [{'colspan':1, 'rowspan':5}, {'colspan': 5, 'rowspan':5}] + [None,]*4,
            [None,]*6,
            [None,]*6,
            [None,]*6,
            [None,]*6,
        ],
        # shared_xaxes='all',
        # shared_yaxes='all',
        # print_grid=True,
        vertical_spacing=0.075,
        horizontal_spacing=0.08
    )

    fig.add_trace(
        go.Bar({
            'x':list(range(data['n_hodo_x'])),
            'y':data['integrals_hodo_x']
        }),
        row = 1, col=2
    )

    fig.add_trace(
        go.Bar({
            'y':list(range(data['n_hodo_y']))[::-1],
            'x':data['integrals_hodo_y'],
            },
            orientation='h'
        ),
        row = 2, col=1
    )

    arri = np.zeros((data['n_hodo_x'], data['n_hodo_y']), dtype=int)
    # print(f'{arri.shape=}, {len(data["integrals_hodo_x"])=}, {len(data["integrals_hodo_y"])=}')
    for i in range(data['n_hodo_y']):
        arri[:,i] += data['integrals_hodo_x']
    for i in range(data['n_hodo_x']):
        arri[i,:] += data['integrals_hodo_y']
    fig.add_trace(
        px.imshow(arri.T[::-1,:]).data[0],
        row = 2, col=2
    )
    # print(f"{data['integrals_hodo_x']=}")
    # print(f"{data['integrals_hodo_y']=}")

    # fig.add_trace(
    #     go.Scatter(
    #         x=[data['odb']['odb_x']],
    #         y=[data['odb']['odb_y']],
    #     ),
    #     row=2, col=2
    # )



    return fig


@callback(
    Output("nai-array", "figure"), 
    Input('traces', 'data')
)
def update_nai(data):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    fig = plotly.subplots.make_subplots(
        rows=4, cols=1,
        shared_xaxes='all',
        shared_yaxes='all',
        # print_grid=True,
    )

    for i, tracei in enumerate(data['traces_nai']):
        samples = list(range(len(tracei)))
        fig.add_trace(go.Scatter(x=samples, y=tracei, name=f'NaI {i}'), row=i+1, col=1 )
    return fig


@callback(
    Output("hodo-hist", "figure"), 
    Input('histograms', 'data')
)
def update_hodo_hist(data):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    fig = plotly.subplots.make_subplots(
        rows=6, cols=6,
        specs = [
            [None, {'colspan': 5, 'rowspan':1}] + [None,]*4,
            [{'colspan':1, 'rowspan':5}, {'colspan': 5, 'rowspan':5}] + [None,]*4,
            [None,]*6,
            [None,]*6,
            [None,]*6,
            [None,]*6,
        ],
        # shared_xaxes='all',
        # shared_yaxes='all',
        # print_grid=True,
        vertical_spacing=0.075,
        horizontal_spacing=0.08
    )
    hists = jsonpickle.decode(data)
    hi = hists['XY_hodoscope']
    # print(hi./values())

    fig.add_trace(
        helpers.hist_to_plotly_bar(hi.project(0)),
        row = 1, col=2
    )

    fig.add_trace(
        helpers.hist_to_plotly_bar(
            hi.project(1),
            orientation='h',
        ),
        row = 2, col=1
    )

    fig.add_trace(
        helpers.hist_to_plotly_2d(
            # hc, 
            hi,
            name='XY Hodoscope',
        ),
        row=2,col=2,
    )

    return fig

