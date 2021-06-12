# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# Import Libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os

# ################################ STYLESHEET ################################   
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# ################################### TAB1 ###################################    
# Get data
root = os.path.join(os.getcwd(), 'DATA')
df = pd.read_csv(os.path.join(root, 'data_for_dash.csv'), index_col = 0)
elements, stylesheet = [], []

# -------------------------------- STYLESHEET --------------------------------
# -- Group selector
stylesheet.append({'selector': 'node',
                   'style': {'content': 'data(label)'}
                  })
# -- Class selector
stylesheet.append({'selector': '.root',
                   'style': {'background-color': 'blue'}
                  })
stylesheet.append({'selector': '.A',
                   'style': {'width': 'data(size)',
                             'height': 'data(size)'}
                  })
stylesheet.append({'selector': '.program',
                   'style': {'width': 'data(size)',
                             'height': 'data(size)'}
                  })


# --------------------------------- CALLBACKS --------------------------------    
@app.callback(
    dash.dependencies.Output('cytoscape', 'elements'),
    [dash.dependencies.Input('btn', 'n_clicks')],
    [dash.dependencies.State('ibx', 'value')])
def update_output(n_clicks, value):
    if value == "" or int(value) not in (df['JIKWON_NO'].unique()):  # 검색한 직원이 없거나 존재하지 않는 경우
        return []
    
    # Set Jikwon info
    selected_jikwon = int(value)
    data = df[df['JIKWON_NO'] == selected_jikwon]
    selected_name = data['NAME'].unique()[0].rstrip()

    # create nodes
    elements=[]
    # -- Jikwon Node
    elements.append({'data': {'id': selected_name, 'label': selected_name},
                     'classes': 'root',
                     'position': {'x': 150, 'y': 150},
                     'grabbable': False})
    # -- Program Nodes
    for name in list(data['A'].unique()):
        elements.append({'data': {'id': name, 'label': name, 'size': data[data["A"] == name]["A"].count()},
                         'classes': 'A'})

    for name in list(data['프로그램종류'].unique()):
        elements.append({'data': {'id': name, 'label': name, 'size': data[data["프로그램종류"] == name]["프로그램종류"].count()},
                         'classes': 'program'})

    # create edges
    for t in list(data['A'].unique()):
        elements.append({'data': {'source': selected_name, 'target': t}})

    for f, t in zip(list(data['A']), list(data['프로그램종류'])):
        elements.append({'data': {'source': f, 'target': t}})

    return elements

# ################################### TAB2 ###################################    

# --------------------------------- CALLBACKS --------------------------------    


# ################################# LAYOUT ###################################    
app.layout = html.Div(children=[    
    html.H1(children='Data Driven HRM',
            style={'textAlign': 'center'}),
    
    html.Div(className='column', id='tabs-content', children=[
        cyto.Cytoscape(
            id='cytoscape',
            elements=elements,
            stylesheet=stylesheet,
            layout={'name': 'cose'},
            style={'width': '95vh', 'height': '100%'}
        )
    ], style={'width': '49%', 'display': 'inline-block'}),
    
    html.Div(className='column', children=[
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='기술 역량 네트워크', value='tab-1', children=[
                dcc.Input(
                    id='ibx',
                    placeholder='직원번호 검색',
                    type='text',
                    value=''
                ),
                html.Button('조회', id='btn'),
            ]),

            dcc.Tab(label='업무 역량 네트워크', value='tab-2', children=[])
        ])
    ], style={'width': '49%', 'display': 'inline-block'}),
])

# --------------------------------- CALLBACKS --------------------------------    
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
                cyto.Cytoscape(id='cytoscape',
                               elements=elements,
                               layout={'name': 'cose'},
                               style={'width': '1100px', 'height': '500px'},
                               stylesheet=stylesheet)
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])

if __name__ == '__main__':
    app.run_server(debug=True)  # automatically refresh page when code is changed