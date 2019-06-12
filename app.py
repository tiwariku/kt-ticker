from flask import Flask, render_template, request, redirect

app = Flask(__name__)

#decorator from Flask accepts route (where in the website you are) and directs to the correct html. Must function name match html file?
@app.route('/')
def index():
  return render_template('index.html') #requires template file ot be in ./templates/

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/query')
def query():
    return render_template('query.html')

if __name__ == '__main__':
  app.run(port=33507)
