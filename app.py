import sys
from flask import Flask, render_template, request, redirect
import requests
from bokeh.plotting import figure
from bokeh.embed import components
import pandas as pd

app = Flask(__name__)

#decorator from Flask accepts route (where in the website you are) and directs to the correct html. Must function name match html file?
@app.route('/')
def index():
    return render_template('index.html') #requires template file ot be in ./templates/

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'GET':
        return redirect('/')
    elif request.method == 'POST':
        #ticker = request.form['ticker']
        #print(request.form.getlist('features'))#, allow_multiple=True))
        success, retrieved = get_ticker_data(request.form['ticker'])
        if success:
            df = json_to_pandas_df(retrieved)
            script, div = get_plot_script(df,
                    request.form['ticker'],
                    plot_indeces=request.form.getlist('features'))
            return render_template('plot_display.html',
                        ticker=request.form['ticker'],
                        script=script,
                        div=div)
        else:
            #how can I redirect to a page but pass variables?
            return render_template('unretrievable.html',
                    ticker=request.form['ticker'],
                    error=str(retrieved)) 
    else:
        return str('UNKNOWN METHOD FOR ROUTE')


def get_ticker_data(ticker):
    '''
    internal function to handle lookup of ticker data
    Quandl API usage:
        GET https://www.quandl.com/api/v3/datasets/{database_code}/
        {dataset_code}/data.{return_format}

    '''
    #from TDI blog post, v1 API used, don't know about v3 advertised on quandl
    url = 'https://www.quandl.com/api/v3/datasets/WIKI/{}?api_key={}'.format(ticker,
                'oszNL4VNfxT-nA-9NkAb')
    sys.stdout.write(url)
    sys.stdout.flush()
    #this object handles retrieving data from apis
    session = requests.Session()

    #from TDI blog, this adapter says retry if you didn't make it to the
    #route through https. it's just http in the TDI blog, unsure how defaults
    #work in this regard
    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=2))
    
    #retrieve response object from api
    response = session.get(url)
    
    #debug
    #sys.stdout.write('quandl reponse status code: {}\n'.format(response.status_code))
    #sys.stdout.flush()
    if response.status_code != 200:
        sys.stdout.write(response.text)
        #TODO redirect to a page explaining the failure
        sys.stdout.flush()
        return False, response.text 

    #use .json() to convert to json-like dictionary 
    return True, response.json()['dataset']

def json_to_pandas_df(my_json):
    '''
    accepts json-like dict from quantl's api, and converts to a pandas
    dataframe with the appropriate column names adn types
    '''
    #debug
    #sys.stdout.write(str(my_json.keys()))
    #print(my_json['column_names'])
    #sys.stdout.flush()

    #TODO quandl json format specific, there must be a better way to do this 
    #without hardcoding 'data' and 'column_names'
    df = pd.DataFrame(my_json['data'], columns=my_json['column_names'])

    #convert to datetime, no timezone given
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def get_plot_script(df, ticker, plot_indeces=['Open', 'Close']):
    '''
    accepts pandas dataframe with index Date and, by default, column 'Open'
    '''
    def find_ylims(df, plot_indeces):
        buff = 1.2
        ymin = 0
        ymax = ymin
        #TODO select subframe correctly
        for index in plot_indeces:
            ymax = max(df[index].max(), ymax)
        return (buff*ymin, buff*ymax)

    fig = figure(title='%s share behaviour' % ticker,
                x_axis_label='Time',
                y_axis_label='Value',
                x_axis_type='datetime',
                y_range=(find_ylims(df, plot_indeces)))
    #TODO select subframe correctly...
    for index in plot_indeces:
        fig.line(df['Date'], df[index], legend=index)
    script, div = components(fig)
    return script, div

#   def make_check_box_html(plot_indeces=['Open', 'Close']):
#       '''
#       generates html for the checkbox based on what plot indeces are available
#       '''
#       htmlstring = '<p>'
#       checkbox_template = "<input type='checkbox' name='features' value={} />{}<br>\n"
#       for index in plot_indeces:
#           htmlstring += checkbox_template.format(index, index)
#       htmlstring += '</p>'
#       return htmlstring



if __name__ == '__main__':
  app.run(port=33507)
