from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

#decorator from Flask accepts route (where in the website you are) and directs to the correct html. Must function name match html file?
@app.route('/')
def index():
    return render_template('query.html') #requires template file ot be in ./templates/

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'GET':
        return render_template('query.html')
    elif request.method == 'POST':
        return render_template('post.html',ticker=request.form['ticker'])#'you have requested: ' + str(request.form['ticker'])
    else:
        return str('UNKNOWN HTTP METHOD')

def get_ticker_data(ticker):
    '''
    internal function to handle lookup of ticker data
    '''
    return str(ticker)


if __name__ == '__main__':
  app.run(port=33507)
