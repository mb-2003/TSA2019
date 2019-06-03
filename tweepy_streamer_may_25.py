import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import tweetlib

twitter_client = tweetlib.TwitterStreamer()
initvalue=20
to_display=initvalue
tweeter=''
sentifilter=[]
numtweets=1000
globt=[]
inct=[]
sentiment_term=''
posnegsentiment=[0,0,0]
NUMTWEETS=5
THRESH=0.1


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app_colors = {
#    'background': '#0C0F0A',
    'background': '#FFFFFF',
    'text': '#000000',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

app.layout = html.Div([
        html.H3('Live Twitter Sentiment',style={'color':"#000000"}),

        html.H5('Sentiment of Tweets by Subject',style={'color':app_colors['text']}),

####### all about the text display of tweets #######
####### all about the graph of tweets #######

        html.Div(className='row', children=[
                                            html.Div(dcc.Input(id='my-id1', value='Donald Trump', type='text'),style={'color':app_colors['someothercolor']}),


                                            dcc.Slider(id='slider-updatemode1',marks={i: '{}'.format(10 ** i) for i in range(4)}, max=3,value=2,step=0.01, updatemode='drag'),
                                            html.Div(id='updatemode-output-container', style={'margin-top': 20}),
                                            html.Div(dcc.Graph(id='my-graph1'),className='col s12'),
                                            ]),

####### all about the pie chart and text display of tweets #######
        html.Div(className='row', children=[
                html.Div(dcc.Graph(id='sentiment-pie', animate=False), className='col s12 m6 l6', style={'color':app_colors['someothercolor']}),
                                            html.Div(dcc.Dropdown(options=[{'label': 'Positive', 'value': 'Positive'},{'label': 'Negative', 'value': 'Negative'},{'label': 'Neutral', 'value': 'Neutral'}],multi=True,value=['Positive'],id='my-dropdown'),className='col s12 m6 '),
                                            html.Div(id='output-container'),

                                            html.Div(id="recent-tweets-table", className='col s12 m6'),
                                            dcc.Interval(id='recent-table-update',interval=1000),
                                            dcc.Interval(id='interval-component',interval=1*1000)]),
        dcc.Interval(id='sentiment-pie-update',interval=60*1000),

####### all about the sentiment by tweeter #######
        html.Div(className='row', children=[html.H5('Sentiment of Tweets by Tweeter',style={'color':app_colors['text']}),
                                            html.Div(id='slider-output-container'),
                                            dcc.Slider(id='slider-updatemode',marks={i: '{}'.format(i) for i in range(10,110,10)}, max=110,value=initvalue,step=10, updatemode='drag'),

                                            html.Div(dcc.Input(id='my-id', value='@realdonaldtrump', type='text'),style={'color':app_colors['someothercolor']}),
                                            dcc.Interval(id='icomponent',interval=1000),
                                            html.Div(dcc.Graph(id='my-graph'),className='col s12'),
                                            ]),

        ], style={'backgroundColor': app_colors['background']})


#########################################################################################
@app.callback(
    Output('updatemode-output-container', 'children'),
    [Input('slider-updatemode1', 'value')])
def update_output(value):
    global numtweets
    numtweets=round(10**value)
    return 'Displaying {} tweets'.format(numtweets)

#########################################################################################
@app.callback(
    Output('output-container', 'children'),
    [Input('my-dropdown', 'value')])
def update_output(value):
    global sentifilter
    sentifilter=value
    return 'Displaying {} tweets'.format(value)

#########################################################################################
@app.callback(
    Output('slider-output-container', 'children'),
    [Input('slider-updatemode', 'value')])
def update_output(value):
    global to_display
    global tweeter
    to_display = value
    return 'Displaying {} tweets'.format(value)

#########################################################################################
@app.callback(Output('sentiment-pie', 'figure'),
              [Input('my-id1','value'),Input('interval-component', 'n_intervals')])
def update_pie_chart(sentiment_term,ninterval):
    # get data from cache
    global globt
    global inct
    global posnegsentiment
    if (len(inct)>0):
        for g in inct:
            if (len(g)>0):
                if (g[1]>THRESH):
                    posnegsentiment[0]+=1
                elif (g[1]<-THRESH):
                    posnegsentiment[1]+=1
                else:
                    posnegsentiment[2]+=1

    labels = ['Positive','Negative','Neutral']
    values = [posnegsentiment[0],posnegsentiment[1],posnegsentiment[2]]

    colors = ['green', 'red', 'blue']
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
    global globt
    return generate_table(globt, max_rows=10)

def quick_color(s):
    # except return bg as app_colors['background']
    if not s:
        return "#000000"

    if s[0][1] >= THRESH:
        # positive
        return "green" #"#007F25"
    elif s[0][1] <= -THRESH:
        # negative:
        return "red" # "#800000"
    else:
        return "blue"

def generatedata(d):
    if (d):
#        print (html.Td(d[0][3]), html.Td("{}".format(d[0][0])), html.Td(d[0][1]))
        return (html.Td(d[0][3]),html.Td("{}".format(d[0][0])), html.Td(d[0][1]))
    else:
        return (html.Td(""),html.Td(""), html.Td(""))

def createdata(df):
    if (len(df)<NUMTWEETS): 
        return df
    else:
        r=[]
        for d in df[len(df)-NUMTWEETS:len(df)-1]:
            if (d[0][1] > THRESH) and 'Positive' in sentifilter:
                r.append(d)
            if (d[0][1] < -THRESH) and 'Negative' in sentifilter:
                r.append(d)
            if (d[0][1] < THRESH) and (d[0][1] > -THRESH) and 'Neutral' in sentifilter:
                r.append(d)
        return r

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
                                  children=generatedata(d), style={'color':"#FFFFFF",
                                                                   'background-color':quick_color(d)}
                                  )
                               for d in createdata(df)])
                          ]
    )

#########################################################################################
@app.callback(
    Output('my-graph', 'figure'),
    [Input('my-id', 'value'),Input('icomponent', 'n_intervals')])
################################################################################
def update_output_div(input_value,n_interval):
    global tweeter

    twitter_client = tweetlib.TwitterClient()
    t=twitter_client.get_user_timeline_tweets(to_display,input_value)
    tweeter=input_value

    num=[]
    pol=[]
    i=0
    if (len(t)>0):
        
        for eacht in t:
            num+=[i]
            pol+=[eacht[1]]
            i+=1
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
def update_output_div1(input_value,niterval):
    global globt
    global inct
    global posnegsentiment
    global twitter_client
    global numtweets
    global sentiment_term

    if (sentiment_term!=input_value):
        globt=[]
        inct=[]
        posnegsentiment=[0,0,0]
#        print ("disconnecting and reconnecting with "+input_value+sentiment_term)
        sentiment_term=input_value
        twitter_client.twitterStream.disconnect()
        del twitter_client.twitterStream
        del twitter_client
        twitter_client = tweetlib.TwitterStreamer()
#        print(input_value
        twitter_client.stream_tweets(input_value)
        
    fetched_tweets_filename="tweets.json"
#    
    twitter_listener=tweetlib.TwitterListener(fetched_tweets_filename)
    inct=twitter_listener.process_tweets()
#    print(inct)
    for t in inct:
        if [t] not in globt:
#            print (t)
            globt.append([t])
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
        xstart=0
        xend=min(len(stream_num)-1,numtweets)
        ystart=max(0,len(stream_pol)-numtweets)
        yend=len(stream_pol)-1
#        print (xstart,xend, ystart, yend, numtweets)
        return {
            'data': [go.Scatter(x=stream_num[xstart:xend],y=stream_pol[ystart:yend],mode='lines+markers')],
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
