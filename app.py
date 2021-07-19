from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'classmysql.engr.oregonstate.edu'
app.config['MYSQL_USER'] = os.environ.get("CS340DBUSER")
app.config['MYSQL_PASSWORD'] = os.environ.get("CS340DBPW")
app.config['MYSQL_DB'] = os.environ.get("CS340DB")
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql = MySQL(app)
    
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
    cur = mysql.connection.cursor()
    cur.execute('''SELECT Fighters.fighterName, SUM(Wins.WinCount) as `Total Fights Won` FROM 
(SELECT fighter1 as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1
UNION 
 SELECT fighter2 as fighterID, COUNT(fightID) as WinCounts  FROM Fights WHERE fighter2Won GROUP BY fighter2) AS Wins
INNER JOIN Fighters
ON Wins.fighterID = Fighters.fighterID
GROUP BY Wins.fighterID
ORDER BY Wins.WinCount DESC
LIMIT 3;''')
    leaders = cur.fetchall()
    return render_template('results.html', leaderboard=leaders)
      
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