import dash
from dash import Dash, html, dcc
from dash import Dash, dcc, html, Input, Output, callback
import plotly 
import zmq
import json
import dash_daq as daq
import ast


app = Dash(__name__, use_pages=True)

print("Connecting to hello world server...")
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

app.layout = html.Div([
    dcc.Store(id='traces'),
    dcc.Interval(id = 'update-data',
                 interval=10*1000, # in milliseconds
                 n_intervals=0),
    # dcc.

    html.H1('Multi-page app with Dash Pages'),
    html.Div([
        daq.BooleanSwitch(id='do-update', on=True,label='Update Data'),
        dcc.Slider(
                id='update-rate',
                min=1,
                max=20,
                step=1,
                value=5
            ),
    ]),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    # html.Div([
    #     html.H4(id='store-dump')
    # ]),
    dash.page_container
])

@callback(Output('update-data', 'interval'), Input('update-rate', 'value' ))
def update_refresh_rate(rate):
    return int(rate)*1000

@callback(Output('traces', 'data'),
        Input('update-data', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('traces', 'data'),
)
def update_metrics(n, do_update, existing_data):
    # print(type(existing_data))
    if(do_update):
        # TODO: make this robust against timeout
        socket.send_string("Hello")
        # dicti = {'n':n}
        message = socket.recv().decode()

        # print(f"Received reply: {message[:10]}...{message[-10:]}")
        dicti = json.loads(message)
        # print('type dicti:', type(dicti))
        # print(dicti[:10])
        return ast.literal_eval(dicti)
    else:
        return existing_data

# @callback(Output('store-dump', 'children'), Input('traces', 'data'))
# def update_header(data):
#     return [html.H1('Current store value:' + f'{data}')]

if __name__ == '__main__':
    app.run(debug=True)