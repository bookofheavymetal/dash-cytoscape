import json
import os
import random

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import dash_extensions.enrich as dee
import dash_bootstrap_components as dbc

import dash_cytoscape as cyto

asset_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'assets'
)

app = dee.DashProxy(__name__, assets_folder=asset_path, transforms=[dee.MultiplexerTransform()])

# app = dash.Dash(__name__, assets_folder=asset_path)
server = app.server

random.seed(2019)

nodes = [
    {'data': {'id': str(i), 'label': 'Node {}'.format(i)}, 'grabbable': False, 'selectable': True}
    for i in range(1, 21)
]

edges = [
    {'data': {'source': str(random.randint(1, 20)), 'target': str(random.randint(1, 20))}, 'selectable': True}
    for _ in range(30)
]

default_elements = nodes + edges

styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 115px)'}
}

app.layout = html.Div([
    html.Div(className='eight columns', children=[
        cyto.Cytoscape(
            id='cytoscape',
            autolock=False,
            elements=default_elements,
            layout={
                'name': 'breadthfirst'
            },
            style={
                'height': '95vh',
                'width': '90%'
            },
            stylesheet=[
                {
                    'selector': 'edge',
                    'style': {
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier'
                    }
                },
                {
                    'selector': 'node',
                    'style': {
                        'label': 'data(label)'
                    }
                }
            ]
        )
    ]),

    html.Div(className='four columns', children=[
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='Actions', children=[
                dbc.Col(
                    children=[
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[
                                        html.Button(
                                            'Remove Selected Nodes',
                                            id='remove-nodes-button',
                                            style={'width': '330px'}
                                        )
                                    ],
                                    style={'width': '330px'}
                                ),
                                dbc.Col(
                                    children=[
                                        html.Button(
                                            'Rename Selected Node',
                                            id='rename-node-button',
                                            style={'width': '330px'}
                                        )
                                    ],
                                    style={'width': '330px'})
                            ]
                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    children=[
                                        html.Button(
                                            'Remove Selected Edges',
                                            id='remove-edges-button',
                                            style={'width': '330px'}
                                        )
                                    ],
                                    style={'width': '330px'}),
                                dbc.Col(
                                    children=[
                                        html.Button(
                                            'Add New Edge',
                                            id='add-new-edge-button',
                                            style={'width': '330px'}
                                        )
                                    ],
                                    style={'width': '330px'})
                            ]
                        )
                    ],
                ),
                dbc.Col([
                    dbc.Row(
                        dbc.Fade(
                            id='current-name',
                            children=[
                                dbc.Toast(
                                    children=[
                                        html.P(
                                            id='current-name-value'
                                        )
                                    ],
                                    header='Current name'
                                )
                            ],
                        )
                    ),
                    dbc.Row(
                        dbc.Fade(
                            id='new-name',
                            children=[
                                dbc.Toast(
                                    children=[
                                        dcc.Input(
                                            id='new-name-value',
                                            type='text',
                                            debounce=True
                                        )
                                    ],
                                    header='New name'
                                )
                            ],
                        )
                    ),
                    dbc.Row(
                        dbc.Fade(
                            id='rename-node-dialogue',
                            children=[
                                dbc.Button(
                                    'Cancel',
                                    id='cancel-rename-node-button'
                                ),
                                dbc.Button(
                                    'Apply',
                                    id='apply-rename-node-button',
                                    disabled=False
                                )
                            ],
                        )
                    )
                ]),
                dbc.Col([
                    dbc.Row(
                        dbc.Fade(
                            id='source-node',
                            children=[
                                dbc.Toast(
                                    children=[
                                        html.P(
                                            id='source-node-label'
                                        )
                                    ],
                                    header='Source node'
                                )
                            ],
                        )
                    ),
                    dbc.Row(
                        dbc.Fade(
                            id='target-node',
                            children=[
                                dbc.Toast(
                                    children=[
                                        html.P(
                                            id='target-node-label'
                                        )
                                    ],
                                    header='Target node'
                                )
                            ],
                        )
                    ),
                    dbc.Row(
                        dbc.Fade(
                            id='create-new-edge-dialogue',
                            children=[
                                dbc.Button(
                                    'Cancel',
                                    id='cancel-create-new-edge-button'
                                ),
                                dbc.Button(
                                    'Apply',
                                    id='apply-create-new-edge-button',
                                    disabled=False
                                )
                            ],
                        )
                    )
                ]),

            ]),
            dcc.Tab(label='Tap Data', children=[
                html.Div(style=styles['tab'], children=[
                    html.P('Node Data JSON:'),
                    html.Pre(
                        id='tap-node-data-json-output',
                        style=styles['json-output']
                    ),
                    html.P('Edge Data JSON:'),
                    html.Pre(
                        id='tap-edge-data-json-output',
                        style=styles['json-output']
                    )
                ])
            ]),

            dcc.Tab(label='Selected Data', children=[
                html.Div(style=styles['tab'], children=[
                    html.P('Node Data JSON:'),
                    html.Pre(
                        id='selected-node-data-json-output',
                        style=styles['json-output']
                    ),
                    html.P('Edge Data JSON:'),
                    html.Pre(
                        id='selected-edge-data-json-output',
                        style=styles['json-output']
                    )
                ])
            ])
        ]),

    ]),
    html.Div([
        dcc.ConfirmDialog(id='too-many-nodes', message='Can\'t rename more than one node')
    ])
])


@app.callback(
    dee.Output('cytoscape', 'elements'),
    [dee.Input('remove-nodes-button', 'n_clicks')],
    [State('cytoscape', 'elements'),
    State('cytoscape', 'selectedNodeData')]
)
def remove_selected_nodes(_, elements, data):
    if elements and data:
        print(data)
        ids_to_remove = {ele_data['id'] for ele_data in data}
        # print("Before:", elements)
        new_elements = [ele for ele in elements if ele['data']['id'] not in ids_to_remove]
        # print("After:", new_elements)
        return new_elements

    return elements


@app.callback(
    dee.Output('cytoscape', 'elements'),
    [dee.Input('remove-edges-button', 'n_clicks')],
    [State('cytoscape', 'elements'),
    State('cytoscape', 'selectedEdgeData')]
)
def remove_selected_edges(_, elements, data):
    if elements and data:
        ids_to_remove = {ele_data['id'] for ele_data in data}
        # print("Before:", elements)
        new_elements = [ele for ele in elements if ele['data']['id'] not in ids_to_remove]
        # print("After:", new_elements)
        return new_elements

    return elements


@app.callback(
    [dee.Output('cytoscape', 'elements'),
    dee.Output('too-many-nodes', 'displayed'),
    dee.Output('new-name', 'is_in'),
    dee.Output('current-name', 'is_in'),
    dee.Output('current-name-value', 'children'),
    dee.Output('rename-node-dialogue', 'is_in')],
    [dee.Input('rename-node-button', 'n_clicks')],
    [State('cytoscape', 'elements'),
    State('cytoscape', 'selectedNodeData')]
)
def show_form_rename_selected_node(_, elements, data):
    if elements and data:
        id_to_rename = {ele_data['id'] for ele_data in data}
        label_to_replace = {ele_data['label'] for ele_data in data}
        if len(id_to_rename) > 1:
            return dash.no_update, True, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        else:
            for elem in elements:
                if elem['data']['id'] in id_to_rename:
                    continue
                else:
                    elem['selectable'] = False
            return elements, False, True, True, list(label_to_replace)[0], True

    return dash.no_update, False, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(
    [dee.Output('cytoscape', 'elements'),
    dee.Output('new-name', 'is_in'),
    dee.Output('current-name', 'is_in'),
    dee.Output('rename-node-dialogue', 'is_in')],
    [dee.Input('cancel-rename-node-button', 'n_clicks')],
    [State('cytoscape', 'elements')]
)
def cancel_renaming_node(_, elements):
    if _ and elements:
        for elem in elements:
            elem['selectable'] = True
        return elements, False, False, False
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(
    [dee.Output('cytoscape', 'elements'),
    dee.Output('new-name-value', 'value'),
    dee.Output('new-name', 'is_in'),
    dee.Output('current-name', 'is_in'),
    dee.Output('rename-node-dialogue', 'is_in')],
    [dee.Input('new-name-value', 'value'),
    dee.Input('apply-rename-node-button', 'n_clicks')],
    [dee.State('cytoscape', 'elements'),
    dee.State('cytoscape', 'selectedNodeData')]
)
def apply_renaming_node(new_name, _, elements, data):
    if new_name and _ not in {None, ''} and elements and data:
        id_to_rename = {ele_data['id'] for ele_data in data}
        for elem in elements:
            if elem['data']['id'] in id_to_rename:
                elem['data']['label'] = new_name
            else:
                elem['selectable'] = True
        return elements, '', False, False, False
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(
    [dee.Output('source-node', 'is_in'),
    dee.Output('target-node', 'is_in'),
    dee.Output('create-new-edge-dialogue', 'is_in')],
    dee.Input('add-new-edge-button', 'n_clicks')
)
def show_form_create_new_edge(_):
    if _:
        return True, True, True
    else:
        return dash.no_update, dash.no_update, dash.no_update


@app.callback(
    dee.Output('source-node-label', 'children'),
    dee.Input('source-node', 'is_in'),
    [dee.State('cytoscape', 'elements'),
    dee.State('cytoscape', 'selectedNodeData')]
)
def source_node(source_node, elements, data):
    if elements and data:
        # id_to_rename = {ele_data['id'] for ele_data in data}
        label_to_replace = {ele_data['label'] for ele_data in data}
        return list(label_to_replace)[0]
    else:
        return dash.no_update


@app.callback(
    dee.Output('target-node-label', 'children'),
    dee.Input('cytoscape', 'selectedNodeData'),
    [dee.State('cytoscape', 'elements'),
    dee.State('source-node-label', 'children')]
)
def target_node(data, elements, source_node):
    if elements and data and source_node:
        # id_to_rename = {ele_data['id'] for ele_data in data}
        label_to_replace = {ele_data['label'] for ele_data in data if ele_data['label'] != source_node}
        return list(label_to_replace)[0]
    else:
        return dash.no_update



@app.callback(
    Output('tap-node-data-json-output', 'children'),
    [Input('cytoscape', 'tapNodeData')]
)
def display_tap_node_data(data):
    return json.dumps(data, indent=2)


@app.callback(
    Output('tap-edge-data-json-output', 'children'),
    [Input('cytoscape', 'tapEdgeData')]
)
def display_tap_edgeData(data):
    return json.dumps(data, indent=2)


@app.callback(
    Output('selected-node-data-json-output', 'children'),
    [Input('cytoscape', 'selectedNodeData')]
)
def display_selected_node_data(data):
    return json.dumps(data, indent=2)


@app.callback(
    Output('selected-edge-data-json-output', 'children'),
    [Input('cytoscape', 'selectedEdgeData')]
)
def display_selected_edge_data(data):
    return json.dumps(data, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True, port='8051', host='0.0.0.0')
