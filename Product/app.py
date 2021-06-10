'''
#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, send_from_directory
from dash import Dash
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import dash_html_components as html

server=Flask(__name__, static_url_path='')
dash_app=Dash(__name__, server=server, url_base_pathname='/dashboard/')
dash_app.layout = html.Div([html.H1('Hi there, I am app1 for dashboards')])
@server.route("/")
def root():
    return server.send_static_file('index.html')

@server.route('/dashboard')
def render_dashboard():
    return flask.redirect('/dash1')

app=DispatcherMiddleware(server, {
    '/dash1':dash_app.server
})

if __name__=="__main__":
    server.run()
'''

# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os
from extra import conversions


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

# set data
root = os.path.join(os.getcwd(), '../민서/DATA')
df = pd.read_csv(os.path.join(root, 'data_for_dash.csv'), index_col=0)
elements = []

app.layout = html.Div(children=[
    html.H1(children='Data Driven HRM',
            style={'textAlign': 'center'}),

    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='업무 네트워크', value='tab-1'),
        dcc.Tab(label='관계도 네트워크', value='tab-2'),
    ]),

    html.Div(id='tabs-content'),
])


@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dcc.Input(
                id='ibx',
                placeholder='직원번호 검색',
                type='text',
                value=''
            ),
            html.Button('조회', id='btn'),

            cyto.Cytoscape(
                id='cytoscape',
                layout={'name': 'cose'},
                style={'width': '100%', 'height': '600px'},
                stylesheet=[{
                    'selector': '.terminal',
                    'style': {
                        'content': 'data(label)',
                        'background-fit': 'cover',
                        'background-image': 'data(url)'
                    },
                }, {
                    'selector': '.people',
                    'style': {
                        'content': 'data(label)',
                    },
                }],
                elements=elements,
            )
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.Iframe(src='./static/index.html',
                        style={"width": "100%", "height": "600px"})
        ])


@app.callback(
    dash.dependencies.Output('cytoscape', 'elements'),
    [dash.dependencies.Input('btn', 'n_clicks')],
    [dash.dependencies.Input('ibx', 'n_submit')],
    [dash.dependencies.State('ibx', 'value')]
)
def update_output(n_clicks, value):
    if value == "" or int(value) not in (df['JIKWON_NO'].unique()):
        return []
    selected_jikwon = int(value)
    data = df[df['JIKWON_NO'] == selected_jikwon]
    selected_name = data['NAME'].unique()[0].rstrip()

    elements = [{
        'data': {'id': selected_name, 'label': selected_name},
        'position': {'x': 150, 'y': 150},
        'grabbable': False,
        'classes': 'people',
        'size': 50}]

    # create nodes
    for name in list(data['A'].unique()) + list(data['프로그램종류'].unique()):
        elements.append(
            {
                'classes': 'terminal',
                'data': {
                    'id': name,
                    'label': name,
                    'url': 'url(/assets/' + conversions.get(name, "progress") + '.png)'
                }})

    # create edges
    for t in list(data['A'].unique()):
        elements.append({'data': {'source': selected_name, 'target': t}})

    for f, t in zip(list(data['A']), list(data['프로그램종류'])):
        elements.append({'data': {'source': f, 'target': t}})

    return elements


if __name__ == '__main__':
    app.run_server(debug=True)  # automatically refresh page when code is changed
