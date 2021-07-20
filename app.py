from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request
from waitress import serve

import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'classmysql.engr.oregonstate.edu'
app.config['MYSQL_USER'] = os.environ.get("CS340DBUSER")
app.config['MYSQL_PASSWORD'] = os.environ.get("CS340DBPW")
app.config['MYSQL_DB'] = os.environ.get("CS340DB")
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

serve(wsgiapp, listen='*:61557')
mysql = MySQL(app)
    
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')   
    
@app.route('/fighters')
def fighters():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT f.fighterName, f.fighterID, (IFNULL(w.weaponName, 'No Weapon')) as `weapon`  FROM Fighters as f
        LEFT JOIN Weapons as w
        on f.weapon=w.weaponID
        ORDER BY f.fighterName asc;''')
    fighters = cur.fetchall()
    
    return render_template('fighters.html', fighters=fighters) 
    
@app.route('/weapons')
def weapons():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT w.weaponName, w.weaponID, w.weaponType, IF(w.ranged=1, "Yes", "No") as ranged,
        IFNULL(GROUP_CONCAT(f.fighterName), "No Users") as `WeaponUsers`
        FROM Weapons w
        LEFT JOIN Fighters as f 
        ON w.weaponID=f.weapon
        GROUP BY w.weaponID;''')
    weapons = cur.fetchall()

    return render_template('weapons.html', weapons=weapons)
    
@app.route('/results')
def results():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT Fighters.fighterName, SUM(Wins.WinCount) as `Total` FROM 
        (SELECT fighter1 as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1
        UNION 
         SELECT fighter2 as fighterID, COUNT(fightID) as WinCounts  FROM Fights WHERE fighter2Won GROUP BY fighter2) AS Wins
        INNER JOIN Fighters
        ON Wins.fighterID = Fighters.fighterID
        GROUP BY Wins.fighterID
        ORDER BY Wins.WinCount DESC
        LIMIT 3;''')
    leaders = cur.fetchall()
    return render_template('results.html', leaders=leaders)
      
@app.route('/fights')
def fightsetup():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT one.fightID, one.fightDate, one.fighter1, two.fighter2, IF(one.fighter1Won=1, one.fighter1, IF(one.fighter2Won=1, two.fighter2, "No Winner")) as winner,
        IFNULL(Prizes.prizeType, "No Prize") as prize FROM

        (SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter1, Fights.fighter1Won, Fights.fighter2Won, Fights.prize
        FROM Fights
        LEFT JOIN Fighters
        on Fights.fighter1=Fighters.fighterID) as one

        JOIN

        (SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter2
        FROM Fights
        LEFT JOIN Fighters
        ON Fights.fighter2=Fighters.fighterID) AS two
        LEFT JOIN Prizes 
        ON one.prize=Prizes.prizeID
        WHERE one.fightID=two.fightID

        ORDER BY one.fightDate desc;;''')
    fights = cur.fetchall()

    return render_template('fights.html', fights=fights)
    
@app.route('/prizes')
def prizes():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT p.prizeID, p.prizeType, IFNULL(f.fighterID, 'No Winners Yet') as fighterID, IFNULL(f.fighterName, 'No Winners Yet') as fighterName
        FROM Prizes as p 
        LEFT JOIN PrizesWon as pw ON p.prizeID=pw.prizeID
        JOIN Fighters as f 
        ON pw.fighterID=f.fighterID;''')
    prizesWon = cur.fetchall()

    return render_template('prizes.html', prizesWon=prizesWon)


    
if __name__ == '__main__':
    app.run(host="http://flip3.engr.oregonstate.edu/", port=61557, debug=False)