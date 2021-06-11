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
df = pd.read_csv(os.path.join(root, 'data_for_dash2.csv'), index_col = 0, encoding='cp949')
df_jikwon = pd.read_csv(os.path.join(root, 'jikwon.csv'), index_col = 0, encoding='cp949')
elements, stylesheet = [], []

MAX_NODE_SIZE = 40 # 최대 node 사이즈 (50)
MIN_NODE_SIZE = 10 # 최소 node 사이즈 (10)

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
                        "font-size": 0}
                  })
stylesheet.append({'selector': '.A:selected',
                   'style': {
                        "font-size": 7
                        }
                  })

stylesheet.append({'selector': '.program',
                   'style': {
                        "font-size": 7
                        }
                  })

# --------------------------------- CALLBACKS --------------------------------    
# 행번 입력 후 조회버튼 클릭 -> node, edge 생성
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
    elements.append({'data': {'id': selected_name, 'label': selected_name, 'size': 30},
                    'classes': 'root',
                    'position': {'x': 150, 'y': 150},
                    'grabbable': False})

    # -- Program Nodes
    data_max = max(data['A'].value_counts().max(), data['프로그램종류'].value_counts().max())
    for name in list(data['A'].unique()):
        elements.append({'data': {'id': name, 'label': name,
                         'size': data[data["A"] == name]["A"].count() / data_max * MAX_NODE_SIZE + MIN_NODE_SIZE},
                         'classes': 'A'})

    for name in list(data['프로그램종류'].unique()):
        elements.append({'data': {'id': name, 'label': name, 
                         'size': data[data["프로그램종류"] == name]["프로그램종류"].count() / data_max * MAX_NODE_SIZE + MIN_NODE_SIZE},
                         'classes': 'program'})

    # create edges
    for t in list(data['A'].unique()):
        elements.append({'data': {'source': selected_name, 'target': t}})

    for f, t in zip(list(data['A']), list(data['프로그램종류'])):
        elements.append({'data': {'source': f, 'target': t}})
    
    return elements


# 행번 입력 후 조회버튼 클릭 -> 직원정보 출력
@app.callback(
    dash.dependencies.Output('jikwon', 'children'),
    [dash.dependencies.Input('btn', 'n_clicks')],
    [dash.dependencies.State('ibx', 'value')])
def update_jikwon_output(n_clicks, value):
    if value == "" or int(value) not in (df['JIKWON_NO'].unique()):  # 검색한 직원이 없거나 존재하지 않는 경우
        return "해당하는 직원정보가 없습니다."
    
    selected_jikwon = int(value)
    data = df_jikwon.loc[selected_jikwon]
    
    output_jikwon = "이름: " + data['NAME'] + "\n"
    output_jikwon = output_jikwon + "부서: " + data['JEOM_NAME'] + "\n"
    output_jikwon = output_jikwon + "직위: " + data['JIKWHI_NAME'] + "\n"
    output_jikwon = output_jikwon + "주직무: " + data['JUJKMU_NM'] + "\n"
    if data['BUJKMU_RATE'] != 0: # 부직무가 있는 경우
        output_jikwon = output_jikwon + "부직무: " + data['BUJKMU_NM'] + "\n"

    return output_jikwon

# 노드 클릭시 해당하는 프로그램 목록 표시
@app.callback(
    dash.dependencies.Output('program_data', 'children'),
    [dash.dependencies.Input('btn', 'n_clicks')],
    [dash.dependencies.Input('cytoscape', 'tapNodeData')],
    [dash.dependencies.State('ibx', 'value')])
def update_program_output(n_clicks, data, value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return []
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn':
        return []

    selected_jikwon = int(value)
    jikwon_program = df[df['JIKWON_NO'] == selected_jikwon]

    if data['label'] in (df['A'].unique()):
        jikwon_program = jikwon_program['프로그램명'][jikwon_program['A'] == data['label']]
    elif data['label'] in (df['프로그램종류'].unique()):
        jikwon_program = jikwon_program['프로그램명'][jikwon_program['프로그램종류'] == data['label']]
    else:
        return []

    output_program = data['label'] + " 프로그램 목록 \n\n"
    for p in jikwon_program:
        output_program = output_program + p + '\n'
    return output_program


# ################################### TAB2 ###################################    

# --------------------------------- CALLBACKS --------------------------------    


# ################################# LAYOUT ###################################    
app.layout = html.Div(children=[    
    html.H1(children='Data Driven HRM',
            style={'textAlign': 'center'}),
    html.Div(className='column', children=[
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='기술 역량 네트워크', value='tab-1', children=[
                # 직원 조회
                html.Div(children=[
                    dcc.Input(
                        id='ibx',
                        placeholder='직원번호 검색',
                        type='text',
                        value=''
                    ),
                    html.Button('조회', id='btn'),
                ], style={'margin': '10px'}),
                # 직원 정보
                html.Div(children=[
                    html.H5(children="직원정보"),
                    html.Div(id='jikwon', children='', style={'whiteSpace': 'pre-line'})
                ], style={'position': 'absolute', 'z-index': '1'}),
                # 프로그램 목록
                html.Div(className='program_data', id='program_data', children='',
                        style={'width': '20%', 'height': '60vh', 'position': 'absolute', 'right': '5px',
                                'whiteSpace': 'pre-line', 'overflow': 'auto', 'z-index': '1'}),
                #네트워크
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
            ]),

            dcc.Tab(label='업무 역량 네트워크', value='tab-2', children=[])
        ])
    ]),
])

# --------------------------------- CALLBACKS --------------------------------    

if __name__ == '__main__':
    app.run_server(debug=True)  # automatically refresh page when code is changed