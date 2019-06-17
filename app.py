from flask import Flask, render_template, request, redirect
import requests
from bokeh.plotting import figure
from bokeh.embed import components
import pandas as pd
import sys
import json

app = Flask(__name__)

#decorator from Flask accepts route (where in the website you are) and directs to the correct html. Must function name match html file?
@app.route('/')
def index():
    return render_template('index.html') #requires template file ot be in ./templates/

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        ticker = request.form['ticker']
        raw_json = get_ticker_data(ticker, alpha_vantage = False)
        df = json_to_pandas_df(raw_json, alpha_vantage = False)
        script, div = get_plot_script(df, ticker)
        return render_template('graph.html', script=script, div=div)
        return render_template('plot_display.html',
                ticker=ticker,
                api_url=df)
    else:
        return str('UNKNOWN ROUTE')

def get_ticker_data(ticker, alpha_vantage = False):
    '''
    internal function to handle lookup of ticker data
    Quandl API usage:
        GET https://www.quandl.com/api/v3/datasets/{database_code}/
        {dataset_code}/data.{return_format}

    '''
    #from TDI blog post, v1 API used, don't know about v3 advertised on quandl
    url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % ticker
    if alpha_vantage:
        api_key = '5A7C8FNB8WEYQQHU'
        outputsize = 'full'

        #using alpha vantage api b/c tdi people swamped quandl
        api_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&outputsize={}&apikey={}'.format(ticker,
                outputsize, api_key)
    #this object handles retrieving data from apis. I thin there should be a way
    #do this directly in pandas though
    session = requests.Session()
    #from TDI blog, this adapter says retry if you didn't make it to the
    #route through https. it's just http in the TDI blog, unsure how defaults
    # work in this regard
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=2))
    #retrieve response object from api, use .json() to convert to json-like
    #dictionary
    response = session.get(url)
    #data = json.loads(url)
    sys.stdout.write(str(response.status_code))
    sys.stdout.flush()
    return response.json() 


def json_to_pandas_df(my_json, alpha_vantage = False):
    '''
    accepts json-like dict from quantl's api, and converts to a pandas
    dataframe with the appropriate column names adn types
    '''
    if alpha_vantage:
        pass
    else:
        #quandl json specific, there must be a better way to do this
        sys.stdout.write(str(my_json.keys()))
        sys.stdout.flush()
        df = pd.DataFrame(my_json['data'], columns=my_json['column_names'])
        #convert to datetime, no timezone given
        df['Date'] = pd.to_datetime(df['Date'])
    return df

def get_plot_script(df, ticker, plot_indeces=['Open']):
    '''
    accepts pandas dataframe with index Date and, by default, column 'Open'
    '''
    fig = figure(title='%s behaviour' % ticker,
                x_axis_label='Time',
                y_axis_label='Value')
    fig.line(df['Date'],df[plot_indeces[0]])
    script, div = components(fig)
    return script, div
    pass


if __name__ == '__main__':
  app.run(port=33507)
