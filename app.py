from flask import Flask, render_template
from flaskext.mysql import MySQLdb
import os

# Set the variables in our application with those environment variables
host = os.environ.get("CS340DBHOST")
user = os.environ.get("CS340DBUSER")
passwd = os.environ.get("CS340DBPW")
db = os.environ.get("CS340DB")
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
    connect_to_database()
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
	
def connect_to_database(host = host, user = user, passwd = passwd, db = db):
    '''
    connects to a database and returns a database objects
    '''
    db_connection = MySQLdb.connect(host,user,passwd,db)
    return db_connection
    
if __name__ == '__main__':
    app.run(host="localhost", port=61557, debug=True)