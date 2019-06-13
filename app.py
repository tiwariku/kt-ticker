from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)
stock = 'GOOG'
api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % stock #hardcoded to look up google right now
session = requests.Session()
session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))#this can retry failed api requests or something
raw_data = session.get(api_url)

#decorator from Flask accepts route (where in the website you are) and directs to the correct html. Must function name match html file?
@app.route('/')
def index():
    return render_template('query.html') #requires template file ot be in ./templates/

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'GET':
        return render_template('query.html')
    elif request.method == 'POST':
        return render_template('post.html',ticker=request.form['ticker'])#'you have requested: ' + str(request.form['ticker'])
    else:
        return str('UNKNOWN HTTP METHOD')

def get_ticker_data(ticker):
    return str(ticker)


if __name__ == '__main__':
  app.run(port=33507)
