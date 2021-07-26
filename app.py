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
@app.route('/index')
def index():
    return render_template('index.html')   
    
# -------------------------------------------------------------------------------------------------
# Fighters Page
@app.route('/fighters')
def fighters():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT f.fighterName, f.fighterID, (IFNULL(w.weaponName, 'No Weapon')) as `weapon`  FROM Fighters as f
        LEFT JOIN Weapons as w
        on f.weapon=w.weaponID
        ORDER BY f.fighterName asc;''')
    fighters = cur.fetchall()
    
    return render_template('fighters.html', fighters=fighters) 
    
@app.route('/fighters', methods=['POST'])
def add_fighter():
    fighterName = request.form.get('fighter-name') or None
    weapon = request.form.get('fighter-weapon') or None

    try:
        con = mysql.connect
        cur = con.cursor()
        cur.execute('''INSERT INTO Fighters (fighterName, weapon) 
            VALUES (%s, %s);''', (fighterName, weapon))
        con.commit()

    except:
        print("Insert Failed")

    return fighters()

# -------------------------------------------------------------------------------------------------
# Weapons Page
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

@app.route('/weapons', methods=['POST'])
def add_weapon():
    weaponName = request.form.get('weapon-name') or None
    weaponType = request.form.get('weapon-type') or None
    ranged = request.form.get('weapon-ranged')

    try:
        con = mysql.connection
        cur = con.cursor()
        cur.execute('''INSERT INTO Weapons (weaponName, weaponType, ranged) 
            VALUES (%s, %s, %s);''', (weaponName, weaponType, ranged))
        con.commit()
        
    except:
        print("Insert Failed")

    return weapons()

# -------------------------------------------------------------------------------------------------
# Results Page
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
    
@app.route('/filtered_results', methods=['POST'])
def filtered_results():
    fighterName = request.form.get('fighterName') or None
    con = mysql.connection
    cur = con.cursor()
 
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

    cur.execute('''SELECT Fighters.fighterName, SUM(Wins.WinCount) as `Total` FROM 
        (SELECT fighter1 as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1
        UNION 
         SELECT fighter2 as fighterID, COUNT(fightID) as WinCounts  FROM Fights WHERE fighter2Won GROUP BY fighter2) AS Wins
        INNER JOIN Fighters
        ON Wins.fighterID = Fighters.fighterID
        AND Fighters.fighterName = %s
        GROUP BY Wins.fighterID;''', fighterName)
    individual = cur.fetchall()
    return render_template('results.html', leaders=leaders, individual=individual)

      

# -------------------------------------------------------------------------------------------------
# Fights Page
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
        ORDER BY one.fightDate desc;''')
    fights = cur.fetchall()

    return render_template('fights.html', fights=fights)
    
@app.route('/fights', methods=['POST'])
def add_fight():
    if request.form.get('old-fight-id'):
        # add code to edit a fight
        pass
        
    else:
        fighter1 = request.form.get('fighter1-id') or None
        fighter2 = request.form.get('fighter2-id') or None
        prize = request.form.get('prize-id') or None
        fightDate = request.form.get('fight-date') or None

        # print(fightDate)
        try:
            con = mysql.connection
            cur = con.cursor()
            cur.execute('''INSERT INTO Fights (fighter1, fighter2, prize, fightDate) 
                VALUES (%s, %s, %s, %s);''', (fighter1, fighter2, prize, fightDate))
            con.commit()

        except:
            print('Insert Failed')
    
    return fightsetup()

# -------------------------------------------------------------------------------------------------
# Prizes Page
@app.route('/prizes')
def prizes():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT p.prizeID, p.prizeType, IFNULL(f.fighterID, 'No Winners Yet') as fighterID, IFNULL(f.fighterName, 'No Winners Yet') as fighterName
        FROM Prizes as p 
        LEFT JOIN PrizesWon as pw ON p.prizeID=pw.prizeID
        JOIN Fighters as f 
        ON pw.fighterID=f.fighterID;''')
    prizesWon = cur.fetchall()

    cur.execute('''SELECT prizeID, prizeType 
        FROM Prizes;''')
    allPrizes=cur.fetchall()
    
    return render_template('prizes.html', allPrizes=allPrizes, prizesWon=prizesWon)

@app.route('/prizes', methods=['POST'])
def add_prize():
    prizeType = request.form.get('prize-type') or None 
    print(prizeType)

    try:
        con = mysql.connection
        cur = con.cursor()
        cur.execute("INSERT INTO Prizes (prizeType) VALUES(?)",
                                                  (prizeType))
        con.commit()

    except:
        print("Insert Failed")
        print("INSERT INTO Prizes (prizeType) VALUES(?)",
                                                  (prizeType))

    return prizes()
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 61557))
    app.run(port=port, debug=True)