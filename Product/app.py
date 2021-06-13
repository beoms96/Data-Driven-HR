# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# Import Libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
import os

from Product.src.extra import conversions

# ################################ STYLESHEET ################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# ################################### TAB1 ###################################
# Get data
root = os.path.join(os.getcwd(), './data')
df = pd.read_csv(os.path.join(root, 'data_for_dash2.csv'), index_col=0, encoding='UTF8')
df_jikwon = pd.read_csv(os.path.join(root, 'jikwon.csv'), index_col=0, encoding='cp949')
elements, stylesheet = [], []

MAX_NODE_SIZE = 40  # 최대 node 사이즈 (50)
MIN_NODE_SIZE = 10  # 최소 node 사이즈 (10)

# -------------------------------- STYLESHEET --------------------------------
# -- Group selector
stylesheet.append({'selector': 'node',
                   'style': {
                       "width": "data(size)",
                       "height": "data(size)",
                       "content": "data(label)",
                       "text-valign": "center",
                       "text-halign": "center",
                       "background-color": "#777",
                       "text-outline-color": "#777",
                       "text-outline-width": "1px",
                       "color": "#fff",
                       "overlay-padding": "6px",
                       "font-size": 7
                   }
                   })
stylesheet.append({"selector": "node:selected",
                   "style": {
                       "border-width": "6px",
                       "background-color": "#555",
                       "text-outline-color": "#555",
                       "border-color": "#555",
                       "border-opacity": "0.5",
                   }
                   })

# -- Class selector
stylesheet.append({'selector': '.root',
                   'style': {
                       "background-color": "#446cb3",
                       "text-outline-color": "#446cb3",
                       "font-size": 10,
                   }
                   })
stylesheet.append({'selector': '.root:selected',
                   'style': {
                       "background-color": "#446cb3",
                       "text-outline-color": "#446cb3",
                       "border-color": "#446cb3",
                   }
                   })

stylesheet.append({'selector': '.A',
                   'style': {
                       "font-size": 0,
                       'background-fit': 'cover',
                       'background-image': 'data(url)',
                   }
                   })
stylesheet.append({'selector': '.A:selected',
                   'style': {
                       "font-size": 'data(font_size)'  # 7
                   }
                   })

stylesheet.append({'selector': '.program',
                   'style': {
                       "font-size": 'data(font_size)',  # 7,
                       'background-fit': 'cover',
                       'background-image': 'data(url)',
                   }
                   })


# --------------------------------- CALLBACKS --------------------------------
# 행번 입력 후 조회버튼 클릭 -> node, edge 생성
@app.callback(
    dash.dependencies.Output('cytoscape', 'elements'),
    [dash.dependencies.Input('btn', 'n_clicks')],
    [dash.dependencies.Input('ibx', 'n_submit')],
    [dash.dependencies.State('ibx', 'value')])
def update_output(n_clicks, n_submits, value):
    if value == "" or int(value) not in (df['JIKWON_NO'].unique()):  # 검색한 직원이 없거나 존재하지 않는 경우
        return []

    # Set Jikwon info
    selected_jikwon = int(value)
    data = df[df['JIKWON_NO'] == selected_jikwon]
    selected_name = data['NAME'].unique()[0].rstrip()

    program_edge = data.drop_duplicates(['A', '프로그램종류'])[['A', '프로그램종류']]
    program_edge['Counts'] = program_edge.groupby(['A'])['프로그램종류'].transform('count')
    program_edge = program_edge[program_edge['Counts'] != 1]

    # create nodes
    elements = []
    # -- Jikwon Node
    elements.append({'data': {'id': selected_name, 'label': selected_name, 'size': 30},
                     'classes': 'root',
                     'position': {'x': 150, 'y': 150},
                     'grabbable': False
                     })

    # -- Program Nodes
    data_max = max(data['A'].value_counts().max(), data['프로그램종류'].value_counts().max())
    for name in list(data['A'].unique()):
        elements.append({'data': {'id': name,
                                  'label': name,
                                  'url': 'url(/assets/' + conversions.get(name, "progress") + '.png)',
                                  'size': data[data["A"] == name][
                                              "A"].count() / data_max * MAX_NODE_SIZE + MIN_NODE_SIZE,
                                  'font_size': data[data["A"] == name][
                                                   "A"].count() / data_max * MAX_NODE_SIZE + MIN_NODE_SIZE / 3
                                  },
                         'classes': 'A'
                         })

    for name in list(program_edge['프로그램종류'].unique()):
        elements.append({'data': {'id': name,
                                  'label': name,
                                  'url': 'url(/assets/' + conversions.get(name, "progress") + '.png)',
                                  'size': data[data["프로그램종류"] == name][
                                              "프로그램종류"].count() / data_max * MAX_NODE_SIZE + MIN_NODE_SIZE,
                                  'font_size': data[data["A"] == name][
                                                   "A"].count() / data_max * MAX_NODE_SIZE + MIN_NODE_SIZE / 3
                                  },
                         'classes': 'program'
                         })

    # create edges
    for t in list(data['A'].unique()):
        elements.append({'data': {'source': selected_name, 'target': t}})

    for f, t in zip(list(program_edge['A']), list(program_edge['프로그램종류'])):
        elements.append({'data': {'source': f, 'target': t}})

    return elements


# 행번 입력 후 조회버튼 클릭 -> 직원정보 출력
@app.callback(
    dash.dependencies.Output('jikwon', 'children'),
    [dash.dependencies.Input('btn', 'n_clicks')],
    [dash.dependencies.Input('ibx', 'n_submit')],
    [dash.dependencies.State('ibx', 'value')])
def update_jikwon_output(n_clicks, n_submits, value):
    if value == "" or int(value) not in (df['JIKWON_NO'].unique()):  # 검색한 직원이 없거나 존재하지 않는 경우
        return "해당하는 직원정보가 없습니다."

    selected_jikwon = int(value)
    data = df_jikwon.loc[selected_jikwon]

    output_jikwon = "이름: " + data['NAME'] + "\n"
    output_jikwon = output_jikwon + "부서: " + data['JEOM_NAME'] + "\n"
    output_jikwon = output_jikwon + "직위: " + data['JIKWHI_NAME'] + "\n"
    output_jikwon = output_jikwon + "주직무: " + data['JUJKMU_NM'] + "\n"
    if data['BUJKMU_RATE'] != 0:  # 부직무가 있는 경우
        output_jikwon = output_jikwon + "부직무: " + data['BUJKMU_NM'] + "\n"

    return output_jikwon


# 노드 클릭시 해당하는 프로그램 목록 표시
@app.callback(
    dash.dependencies.Output('program_data', 'children'),
    [dash.dependencies.Input('btn', 'n_clicks')],
    [dash.dependencies.Input('cytoscape', 'tapNodeData')],
    [dash.dependencies.Input('ibx', 'n_submit')],
    [dash.dependencies.State('ibx', 'value')])
def update_program_output(n_clicks, data, n_submits, value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return []
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn' or button_id == 'ibx':
        return []

    selected_jikwon = int(value)
    jikwon_program = df[df['JIKWON_NO'] == selected_jikwon]

    if data['label'] in (df['A'].unique()):
        jikwon_program = jikwon_program[['프로그램명', '프로그램설명']][jikwon_program['A'] == data['label']]
    elif data['label'] in (df['프로그램종류'].unique()):
        jikwon_program = jikwon_program[['프로그램명', '프로그램설명']][jikwon_program['프로그램종류'] == data['label']]
    else:
        return []

    return  html.Div([
        html.H2(
            children = data['label'] + " 프로그램 목록",
            style = {
                'margin'        : '5px',
                'paddingBottom': '10px',
                'fontSize'     : '14px',
                'fontWeight'   : 'bold',
                'color'         : '#000'
            }
        ),
        dash_table.DataTable(
                        id="table",
                        data=jikwon_program.to_dict('records'),
                        columns=[
                            {'id': '프로그램명', 'name': '프로그램명'},
                            {'id': '프로그램설명', 'name': '프로그램설명'}
                        ],
                        page_action='none',
                        style_table={'height': '100%', 'overflowY': 'auto'},
                        style_cell={'textAlign': 'left'},
                    )
                ],
                style={
                    'position': 'absolute',
                    'backgroundColor': 'rgba(255,255,255,0.8)',
                    'border': '1px solid #ccc',
                    'zIndex': '20',
                    'right': '0',
                    'width': '20%',
                    'marginTop': '50px',
                    'marginRight': '25px',
                    'padding': '18px 0px 18px 0px',
                    'overflow': 'auto',
                    'whiteSpace': 'pre-line',
                    'height': '80%',
                })


# ################################### TAB2 ###################################

# ################################# LAYOUT ###################################
app.layout = html.Div(children=[
    html.Div(children=[
        html.Img(src=app.get_asset_url('SHbank.png'), style={'height': '3%', 'width': '3%', 'display': 'inline-block'}),
        html.H1(children='  Shinhan Data Driven HRM ', style={'display': 'inline-block'}),
    ], style={'textAlign': 'center'}),

    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='기술 역량 네트워크', value='tab-1', children=[]),
        dcc.Tab(label='업무 역량 네트워크', value='tab-2', children=[])
    ], style={'margin-left': 50, 'margin-right': 50}),

    html.Div(id='tabs-content',
             style={'margin-left': 50, 'margin-right': 50}),
])


# --------------------------------- CALLBACKS --------------------------------
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(
            style={'backgroundColor': '#eee',
                   'border': '1px solid #ccc',
                   'position': 'relative',
                   'fontFamily': 'sans-serif',
                   'fontSize': '12px',
                   'lineHeight': '1.25em',
                   },
            children=[
                # 직원 조회
                html.Div([
                    html.Div(
                        "",
                        id="maintitle",
                        style={
                            'width': '100%',
                            'height': '72px',
                            'backgroundRepeat': 'no-repeat',
                            'marginBottom': '20px',
                        }
                    ),

                    html.H2(
                        children='신한은행 기술 역량 관계도',
                        style={
                            'margin': '0px',
                            'fontSize': '14px',
                            'fontWeight': 'bold',
                            'color': '#000'
                        }
                    ),

                    html.H2(
                        children='(사용 기술스택 기반)',
                        style={
                            'margin': '0px',
                            'paddingBottom': '10px',
                            'fontSize': '14px',
                            'fontWeight': 'bold',
                            'color': '#000'
                        }
                    ),

                    html.Div(
                        '당행 IT 인력들의 역량 기반 개인 네트워크',
                        style={
                            'padding': '6px 0 10px 0',
                            'color': '#000'
                        }
                    ),

                    # 직원 정보
                    html.Div([
                        html.H2(
                            children="직원정보",
                            style={
                                'margin': '0px',
                                'paddingBottom': '10px',
                                'fontSize': '14px',
                                'fontWeight': 'bold',
                                'color': '#000'
                            }
                        ),

                        html.Div(id='jikwon',
                                 children='',
                                 style={'whiteSpace': 'pre-line',
                                        'paddingBottom': '10px',
                                        })

                    ]),

                    html.Div([

                        html.H2(
                            children='Search : ',
                            style={
                                'margin': '0px',
                                'paddingBottom': '10px',
                                'fontSize': '14px',
                                'fontWeight': 'bold',
                                'color': '#000'
                            }
                        ),

                        dcc.Input(
                            id='ibx',
                            placeholder='Search by name',
                            type='text',
                            value='6163718',
                            style={'border': '1px solid #999',
                                   'borderRadius': '0px',
                                   'backgroundColor': '#fff',
                                   'padding': '5px 7px 4px 7px',
                                   'width': '205px',
                                   'height': '26px',
                                   'color': '#000'
                                   }
                        ),

                        html.Button('조회', id='btn', style={"display": "none"}),
                    ],
                        style={"borderTop": "1px solid #999",
                               "padding": "20px 0 0px 2px"
                               }
                    )
                ], style={'width': 'fit-content',
                          'position': 'absolute',
                          'marginTop': '50px',
                          'marginLeft': '25px',
                          'backgroundColor': 'rgba(255,255,255,0.8)',
                          'border': '1px solid #ccc',
                          'zIndex': '1',
                          'padding': '18px 18px 18px 18px',
                          }
                ),

                # 프로그램 목록
                html.Div(id = 'program_data', children=[]),

                # 네트워크
                html.Div([
                    cyto.Cytoscape(
                        id='cytoscape',
                        elements=elements,
                        layout={'name': 'cose',
                                'idealEdgeLength': 30,
                                'nodeRepulsion': 1000,
                                'nodeOverlap': 30,
                                'padding': 30,
                                'componentSpacing': 100,
                                },
                        style={'width': '90%', 'height': '75vh', 'position': 'relative'},
                        stylesheet=stylesheet
                    )
                ]),
            ])
    elif tab == 'tab-2':
        return html.Div([
            html.Iframe(src='./static/index.html',
                        style={"width": "100%", "height": "600px"})
        ])


if __name__ == '__main__':
    app.run_server(debug=True)  # automatically refresh page when code is changed
