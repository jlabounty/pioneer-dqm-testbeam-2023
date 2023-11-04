from dash import Dash, dcc, html, Input, Output, ctx
import plotly.express as px
import plotly.subplots
import plotly.graph_objects as go
import plotly
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import dash
import dash_daq as daq
import dash_bootstrap_components as dbc

# app = Dash(__name__)
dash.register_page(__name__)

layout = html.Div([
    html.H4('Plot of the hodoscopes relative position vs. the LYSO/NaI array'),
    dbc.Row([
        dbc.Col([daq.NumericInput(id='hodo_position_offset_x', min=-1000,max=1000,value=0),]),
        dbc.Col([daq.NumericInput(id='hodo_position_offset_y', min=-1000,max=1000,value=0),]),
        dbc.Col([daq.NumericInput(id='lyso_position_offset_x', min=-1000,max=1000,value=0),]),
        dbc.Col([daq.NumericInput(id='lyso_position_offset_y', min=-1000,max=1000,value=0),]),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="hodo-position"),
        ], width='auto'),
        dbc.Col([
            dbc.Row([
                dcc.Graph(id='trace-array')
            ]),
            dbc.Row([
                dcc.Graph(id='t0-trace')
            ]),
        ], width='auto')
    ])
    # html.Div([
    # ]),
])

@callback(
    Output("hodo-position", "figure"), 
    Input('do-update', 'on'),
    Input('do-update-now', 'n_clicks'), 
    Input("hodo-position", "figure"), 
    Input('traces', 'data'),
    Input('constants', 'data'),
    Input('hodo_position_offset_x','value'),
    Input('hodo_position_offset_y','value'),
    Input('lyso_position_offset_x','value'),
    Input('lyso_position_offset_y','value'),
)
def update_graph(do_update, do_update_now, existing_figure,
                data,
                odb, 
                hodo_position_offset_x,
                hodo_position_offset_y,
                lyso_position_offset_x,
                lyso_position_offset_y
):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    if(not(do_update or ctx.triggered_id in ['do-update-now', 'reset-histograms'])):
        return existing_figure
    fig = plotly.subplots.make_subplots()

    # color_scale = 

    # hodo_position_offset_x = 0
    # hodo_position_offset_y = 0

    # lyso_position_offset_x = 0
    # lyso_position_offset_y = 0

    print(data.keys())
    hodo_width = 2
    hodo_offset_x = hodo_width
    hodo_height = hodo_offset_x * data['n_hodo_x']
    hodo_offset_y = 0

    lyso_width_x = 25.
    lyso_width_y = 25.

    hodo_center_offset = (hodo_offset_x) * data['n_hodo_x'] / 2.0 - hodo_width/2.

    print(
        hodo_position_offset_x,
        hodo_position_offset_y,
        lyso_position_offset_x,
        lyso_position_offset_y
    )
    fig.add_trace(
        go.Scatter(
            x=[-105,105],
            y=[-105,105],
            mode='markers',
            opacity=0.0
        )
    )


    # TODO: get this information from the DB
    lyso_offsets = {
        0:[0.5,0.0],
        1:[1.5,0.0],
        2:[2.5,0.0],
        3:[0.0,1.0],
        4:[1.0,1.0],
        5:[2.0,1.0],
        6:[3.0,1.0],
        7:[0.5,2.0],
        8:[1.5,2.0],
        9:[2.5,2.0],
    }
    lyso_center_offset_x = 4*lyso_width_x/2. 
    lyso_center_offset_y = 3*lyso_width_y/2. 

    for i in range(data['n_lyso']):
        lyso_energy = np.abs(data['integrals_lyso'][i])/250000.
        xtal_offsets = lyso_offsets[i]

        x0 = xtal_offsets[0]*lyso_width_x + lyso_width_x/2. - lyso_center_offset_x - lyso_width_x/2.  + lyso_position_offset_x
        x1 = x0 + lyso_width_x

        y0 = xtal_offsets[1]*lyso_width_y + lyso_width_y/2. - lyso_center_offset_y - lyso_width_y/2. + lyso_position_offset_y
        y1 = y0 + lyso_width_y

        fig.add_shape(type="rect",
            x0=x0, y0=y0, x1=x1, y1=y1,
            line=dict(
                color="Black",
                width=2,
            ),
            fillcolor=px.colors.sample_colorscale('greys',lyso_energy )[0],
            opacity=1,
            # text = f'{lyso_energy:.2f}'
        )

    # add the hodoscope
    for i in range(data['n_hodo_x']):
        hodo_energy = np.abs(data['integrals_hodo_x'][i]/2500000.)
        # if( i == 3):
        #     hodo_energy = 0.7
        x0 = (i)*hodo_offset_x - hodo_width/2. + hodo_position_offset_x - hodo_center_offset
        x1 = x0 + hodo_width

        y0 = (i)*hodo_offset_y - hodo_height/2. + hodo_position_offset_y 
        y1 = y0 + hodo_height

        fig.add_shape(type="rect",
            x0=x0, y0=y0, x1=x1, y1=y1,
            line=dict(
                color="RoyalBlue",
                width=2,
            ),
            fillcolor=px.colors.sample_colorscale("viridis",hodo_energy)[-1],
            opacity=0.2
        )

    for i in range(data['n_hodo_y']):
        hodo_energy = np.abs(data['integrals_hodo_y'][i]/2500000.)
        y0 = i*hodo_offset_x - hodo_width/2. + hodo_position_offset_y - hodo_center_offset
        y1 = y0 + hodo_width

        x0 = i*hodo_offset_y - hodo_height/2. + hodo_position_offset_x
        x1 = x0 + hodo_height

        fig.add_shape(type="rect",
            x0=x0, y0=y0, x1=x1, y1=y1,
            line=dict(
                color="RoyalBlue",
                width=2,
            ),
            fillcolor=px.colors.sample_colorscale("viridis",hodo_energy)[-1],
            opacity=0.2
        )


    # add the NaI xtals
    nai_height = 110
    nai_width  = 50

    nai_positions = [
        [ -lyso_center_offset_x-nai_width, -nai_height/2.,                               -lyso_center_offset_x,          nai_height/2.,                                  0],
        [  lyso_center_offset_x,           -nai_height/2.,                               lyso_center_offset_x+nai_width, nai_height/2.,                                  0],
        [ -nai_height/2,                    lyso_center_offset_y+nai_width,              nai_height/2,                    lyso_center_offset_y,                          0],
        [ -nai_height/2,                    -lyso_center_offset_y-nai_width,                        nai_height/2,                    -lyso_center_offset_y,              0],
    ]

    for x0, y0, x1, y1, energy in nai_positions:
        fig.add_shape(type="rect",
            x0=x0 + lyso_position_offset_x, 
            y0=y0 + lyso_position_offset_y, 
            x1=x1 + lyso_position_offset_x, 
            y1=y1 + lyso_position_offset_y,
            line=dict(
                color="Purple",
                width=2,
            ),
            fillcolor="Purple",
            opacity=0.2
        )






    fig.update_layout(
        autosize=False,
        width=800,
        height=800,
    )

    return fig