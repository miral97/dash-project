# (version 1.0.0)
import dash  # (version 1.9.1) pip install dash==1.9.1
import dash_html_components as html
import requests
import dash_bootstrap_components as dbc
import base64
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State

colors = {
    'background': '#007D99'}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
server = app.server

image_filename_1 = 'pinfo.jpeg'
image_filename_2 = 'resultt.jpeg'
encoded_image_1 = base64.b64encode(open(image_filename_1, 'rb').read())
encoded_image_2 = base64.b64encode(open(image_filename_2, 'rb').read())

image_filename_3 = 'Hnet.com-image (1).png'  # replace with your own image
encoded_image_3 = base64.b64encode(open(image_filename_3, 'rb').read())

game_users_cols = ['name', 'game_user_id', 'shots_count',
                   'missed_shots_count', 'has_next_shot',
                   'id', 'role', 'avatar', 'email']


def get_data(url: str) -> pd.DataFrame:
    kick_requests = requests.get(url)
    json_data = kick_requests.json()
    df = pd.DataFrame(json_data)
    data = []
    for index, row in df.iterrows():
        id = row['id']
        url = f'http://backend-test.northeurope.azurecontainer.io:4001/game/{id}?orderBy=points_ASC&limit=10'
        response = requests.get(url)
        game_request = response.json()
        game_users_list = game_request['gameUsers']
        shots = game_request['shots']
        game_df = get_game_users(game_users_list, cols=["id", "shots_count", "missed_shots_count",
                                                        "has_next_shot", "game_user_id", "role",
                                                        "avatar", "email"])
        if game_df.empty:
            game_df['name'] = [game_request['name']]
        else:
            game_df['name'] = game_request['name']
        game_df = game_df[['name', 'id', 'shots_count', 'missed_shots_count', 'has_next_shot',
                           'game_user_id', 'role', 'avatar', 'email']]

        shot_df = get_shots(shots, cols=['shot_id', 'experience', 'points', 'speed',
                                         'accuracy', 'is_goal', 'video_link', 'preview_link',
                                         'status', 'error_msg', 'created_at', 'updated_at'])
        result = pd.concat([game_df, shot_df], axis=1)
        data.append(result)
    final_df = pd.concat(data)
    return final_df


def get_game_users(game_users: list, cols: list) -> pd.DataFrame:
    if len(game_users) > 0:
        game_users_data = []
        for item in game_users:
            game_users = [item['id'], item['shotsCount'], item['missedShotsCount'],
                          item['hasNextShot'], item['user']['id'],
                          item['user']['role'],
                          item['user']['avatar'], item['user']['email']]
            game_users_data.append(game_users)

        result = pd.DataFrame(game_users_data)
        result.columns = cols
        return result
    else:
        result = pd.DataFrame(columns=cols)
        return result


def get_shots(shots: list, cols: list) -> pd.DataFrame:
    if len(shots) > 0:
        # shots are present
        shots_data = []
        for shot in shots:
            game_shots = [shot['id'], shot['experience'],
                          shot['points'], shot['speed'],
                          shot['accuracy'], shot['isGoal'],
                          shot['videoLink'], shot['previewLink'],
                          shot['status'], shot['errorMsg'],
                          shot['createdAt'], shot['updatedAt']]
            shots_data.append(game_shots)
        result = pd.DataFrame(shots_data)
        result.columns = cols
        return result
    else:
        result = pd.DataFrame(columns=cols)
        return result


url = "http://backend-test.northeurope.azurecontainer.io:4001/games?orderBy=name_ASC&limit=10"
df = get_data(url)
has_next_shot = df[['name', 'id', 'has_next_shot']]

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Header(children='', style={'textAlign': 'center', 'backgroundcolor': '#004d4d', 'font-weight': 'bold'}),

    html.Div([
        html.Img(src='data:Hnet.com-image (1)/png;base64,{}'.format(encoded_image_3.decode())

                 )]),

    html.Div(children='''
             Explore your skills.
             ''', style={'color': 'white', 'font-weight': 'bold'}),
    dbc.CardDeck(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Video ", style={'color': 'white', 'font-weight': 'bold'}, className=""),
                        html.P(
                            "See recorded video here", style={'color': 'white', 'font-weight': 'bold'},
                            className="",
                        ),
                        html.Video(src='https://sckickeracedev.blob.core.windows.net/videos/ckq9f3z5yo9m00p38qzdz5i48.mp4',
                                   controls=True, style={"height": "500px", "width": "100%"})
                        # html.Div(id='target', style={"height": "500px", "width": "100%"})
                        
                        
                
                        # html.Iframe(id='video',
                        #               style={"height": "500px", "width": "100%"})
                        

                    ]

                )
            ),
            
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Results ", style={'color': 'white', 'font-weight': 'bold'}, className=""),
                        html.P(
                            "See results here", style={'color': 'white', 'font-weight': 'bold'},
                            className="",
                        ),
                        html.Div(
                            id='click-data',
                            children=dash_table.DataTable(
                                id='table',
                                data=df.to_dict('records'),
                                columns=[{"name": i, "id": i} for i in df.columns],
                                style_header={'backgroundColor': 'rgb(0, 125, 153)', 'border': '1px solid green'},
                                style_data={'border': '1px solid green'},
                                style_cell={
                                    'backgroundColor': 'rgb(0, 125, 153)',
                                    'color': 'white',
                                    'textAlign': 'left',
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                },
                                style_table={'overflowX': 'auto'},
                            )
                        )
                    ])
            )

        ])
])


# define callback
@app.callback(
    Output('target', 'children'),
    [Input('table', 'active_cell')],
    [State('table', 'data')]
)
def display_click_data(active_cell, table_data):
    if active_cell:
        row = active_cell['row']
        col = active_cell['column_id']
        if col == "video_link":
            value = table_data[row][col]
            return html.Iframe(src=value)
        else:
            out = 'video not selected'
            return out


if __name__ == '__main__':
    app.run_server(debug=True)
