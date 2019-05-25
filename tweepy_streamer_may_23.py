import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import tweetlib

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Input(id='my-id', value='@realdonaldtrump', type='text'),
    html.Div(id='my-div')
])


@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
#########################################################################################





################################################################################
def update_output_div(input_value):
    twitter_client = tweetlib.TwitterClient()
    print(input_value)
    t=twitter_client.get_user_timeline_tweets(1,input_value)
    print(t)
    if (len(t)>0):
        return 'a tweet "{}"'.format(t[0])
#    return 'You\'ve entered "{}"'.format(input_value)


if __name__ == '__main__':
    app.run_server(debug=True)
