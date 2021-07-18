<<<<<<< HEAD
from flask import Flask, render_template
=======
from flask import Flask
from flask import render_template
>>>>>>> f1c3ba5bda4d589f26876d115a464ef3ec5af8e9
app = Flask(__name__)
    
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/index')
def index():
    return render_template('index.html')   
    
@app.route('/fighters')
def fighters():
    return render_template('fighters.html') 
    
@app.route('/weapons')
def weapons():
    return render_template('weapons.html')
    
@app.route('/results')
def results():
    return render_template('results.html')
      
@app.route('/fightsetup')
def fightsetup():
    return render_template('fightsetup.html')
    
@app.route('/prizes')
def prizes():
    return render_template('prizes.html')

@app.route('/test')
def hello_world():
    return 'Hello, World!'
	
if __name__ == '__main__':
    app.run(host="localhost", port=61557, debug=True)