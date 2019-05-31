import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import tweetlib

globt=[]
sentiment_term=['']
posnegsentiment=[0,0]
NUMTWEETS=5
THRESH=0.1


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

app.layout = html.Div([
        html.H3('Live Twitter Sentiment',style={'color':"#CECECE"}),
        html.Div(className='row', children=[html.H5('Sentiment of Tweets by Tweeter',style={'color':app_colors['text']}),
                                            html.Div(dcc.Input(id='my-id', value='@realdonaldtrump', type='text'),style={'color':app_colors['someothercolor']}),
                                            html.Div(dcc.Graph(id='my-graph'),className='col s12 m6 l6'),
                                            html.Div(id="recent-tweets-table", className='col s12 m6 l6'),
                                            dcc.Interval(id='recent-table-update',interval=1000),
                                            ]),

        html.Div(className='row', children=[html.H5('Sentiment of Tweets by Subject',style={'color':app_colors['text']}),
                                            html.Div(dcc.Input(id='my-id1', value='Donald Trump', type='text'),style={'color':app_colors['someothercolor']}),
                                            html.Div(dcc.Graph(id='my-graph1'),className='col s12 m6 l6'),
                                            html.Div(dcc.Graph(id='sentiment-pie', animate=False), className='col s12 m6 l6', style={'color':app_colors['someothercolor']}),
                                            dcc.Interval(id='interval-component',interval=1*1000)]),
        dcc.Interval(
            id='sentiment-pie-update',
            interval=60*1000
        ),
], style={'backgroundColor': app_colors['background']})

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

@app.callback(Output('sentiment-pie', 'figure'),
              [Input('my-id1','value'),Input('interval-component', 'n_intervals')])
def update_pie_chart(sentiment_term,ninterval):
    # get data from cache
    if (len(globt)>0):
        g=globt[len(globt)-1]
        if (len(g)>0):
            if (g[0][1]>THRESH):
                posnegsentiment[0]+=1
            else:
                if (g[0][1]<-THRESH):
                    posnegsentiment[1]+=1

    labels = ['Positive','Negative']
    values = [posnegsentiment[0],posnegsentiment[1]]
#    print (values)
    colors = ['#007F25', '#800000']
    trace = go.Pie(labels=labels, values=values,
                   hoverinfo='label+percent', textinfo='value', 
                   textfont=dict(size=20, color=app_colors['text']),
                   marker=dict(colors=colors, 
                               line=dict(color=app_colors['background'], width=2)))
    return {"data":[trace],'layout' : go.Layout(
                                                  title='Positive vs Negative sentiment for "{}" (longer-term)'.format(sentiment_term),
                                                  font={'color':app_colors['text']},
                                                  plot_bgcolor = app_colors['background'],
                                                  paper_bgcolor = app_colors['background'],
                                                  showlegend=True)}

#########################################################################################
@app.callback(Output('recent-tweets-table', 'children'),
              [Input(component_id='my-id1', component_property='value'),Input('interval-component', 'n_intervals')])
################################################################################              
def update_recent_tweets(sentiment_term,ninterval):
#    if sentiment_term:
#        df = pd.read_sql("SELECT sentiment.* FROM sentiment_fts fts LEFT JOIN sentiment ON fts.rowid = sentiment.id WHERE fts.sentiment_fts MATCH ? ORDER BY fts.rowid DESC LIMIT 10", conn, params=(sentiment_term+'*',))
#    else:
 #       df = pd.read_sql("SELECT * FROM sentiment ORDER BY id DESC, unix DESC LIMIT 10", conn)

#    df['date'] = pd.to_datetime(df['unix'], unit='ms')

#    df = df.drop(['unix','id'], axis=1)
#    df = df[['date','tweet','sentiment']]
    return generate_table(globt, max_rows=10)

def quick_color(s):
    # except return bg as app_colors['background']
    if not s:
        return app_colors['background']
    if s[0][1] >= THRESH:
        # positive
        return "#002C0D"
    elif s[0][1] <= -THRESH:
        # negative:
        return "#270000"
    else:
        return app_colors['background']

def generatedata(d):
    if (d):
        print (html.Td(d[0][3]), html.Td("{}".format(d[0][0])), html.Td(d[0][1]))
        return (html.Td(d[0][3]),html.Td("{}".format(d[0][0])), html.Td(d[0][1]))
    else:
        return (html.Td(""),html.Td(""), html.Td(""))

def createdata(df):
    if (len(df)<NUMTWEETS): 
        return df
    else:
        return df[len(df)-NUMTWEETS:len(df)-1]

def generate_table(df, max_rows=10):
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                    html.Th('Time'),
                                    html.Th('Tweet'),
                                    html.Th('Sentiment'),
                                    ],
                                  style={'color':app_colors['text']}
                                  )
                              ),
                          html.Tbody(
                              [
                              html.Tr(
                                  children=generatedata(d), style={'color':app_colors['text'],
                                                'background-color':quick_color(d)}
                                  )
                               for d in createdata(df)])
                          ]
    )

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
#        print(pol)
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

#############################################################################
@app.callback(
    Output('my-graph1', 'figure'),
    [Input('my-id1', 'value'),Input('interval-component', 'n_intervals')])
################################################################################
def update_output_div(input_value,niterval):

    sentiment_term[0]=input_value
    fetched_tweets_filename="tweets.json"
    twitter_client = tweetlib.TwitterStreamer()
    twitter_client.stream_tweets(input_value)

    twitter_listener=tweetlib.TwitterListener(fetched_tweets_filename)
    for t in twitter_listener.process_tweets():
        if t  not in globt:
            globt.append([t])
#    print (globt)
    stream_num=[]
    stream_pol=[]
    stream_i=0
    if (len(globt)>0):
        for eacht in globt:
            if (len(eacht)>0):
                stream_num+=[stream_i]
                stream_pol+=[eacht[0][1]]
                stream_i+=1
#        print(stream_pol)
        return {
            'data': [go.Scatter(x=stream_num,y=stream_pol,mode='lines+markers')],
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


if __name__ == '__main__':
    app.run_server(debug=True)
