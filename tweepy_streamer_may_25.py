import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import tweetlib

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Input(id='my-id', value='@realdonaldtrump', type='text'),
    dcc.Graph(id='my-graph')
])
#app.layout = html.Div(
#    html.Div([
#        html.H4('Polarity graph'),
#        dcc.Input(id='my-id', value='@realdonaldtrump', type='text'),
#        dcc.Graph(id='live-update-graph'),
#        dcc.Interval(
#            id='interval-component',
#            interval=1*10000, # in milliseconds
#            n_intervals=0
#        )
#    ])
#)



#@app.callback(
#    Output(component_id='my-div', component_property='children'),
#    [Input(component_id='my-id', component_property='value')]
#)
#@app.callback(Output('live-update-graph', 'figure'),
#              [Input('interval-component', 'n_intervals')])

#########################################################################################
@app.callback(
    Output('my-graph', 'figure'),
    [Input('my-id', 'value')])
################################################################################
def update_output_div(input_value):

    twitter_client = tweetlib.TwitterClient()
    t=twitter_client.get_user_timeline_tweets(100,input_value)

    num=[]
    pol=[]
    i=0
    if (len(t)>0):
        for eacht in t:
            num+=[i]
            pol+=[eacht[1]]
            i+=1
        print(pol)
        return {
            'data': [go.Scatter(x=num,y=pol,mode='lines+markers')],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': "Polarity"
            }],
            'yaxis': {'type': 'linear'},
            'xaxis': {'showgrid': False}
        }
    }
    return {}
def update_output_div2(input_value):
    twitter_client = tweetlib.TwitterClient()
#    print(input_value)
    t=twitter_client.get_user_timeline_tweets(100,input_value)
#    print(t)
    if (len(t)>0):
        str='html.Div(['
        for eacht in t:
            str+="html.P(" + "Tweet: {}".format(eacht[0])+"),"
            str+="html.P(" + "Polarity: {}".format(eacht[1])+"),"
            str+="html.P(" + "Subjectivity: {}".format(eacht[2])+")"
        str+='])'
        print (str)
        return str
    return ''.format()
    
#    return 'You\'ve entered "{}"'.format(input_value)


if __name__ == '__main__':
    app.run_server(debug=True)
