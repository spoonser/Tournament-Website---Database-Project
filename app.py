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
    # Get the weapon names to populate the available Weapon choices when creating a new Fighter.
    cur.execute('''SELECT weaponName, weaponID from Weapons''')
    available_weapons = cur.fetchall()
    
    return render_template('fighters.html', fighters=fighters, available_weapons=available_weapons) 
    
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
def modify_weapon():
    if request.form.get('new-weapon'):
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
    
    elif request.form.get('weapon-update'):
        weaponID = request.form.get('weapon-id') or None
        weaponName = request.form.get('weapon-name') or None
        weaponType = request.form.get('weapon-type') or None
        ranged = request.form.get('weapon-ranged')
        try:
            con = mysql.connection
            cur = con.cursor()
            cur.execute('''UPDATE Weapons SET weaponName=%s, weaponType=%s, ranged=%s WHERE weaponID=%s''', (weaponName, weaponType, ranged, weaponID))
            con.commit()
            
        except:
            print("Weapon Update Failed")

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
    
@app.route('/results', methods=['POST'])
def filtered_results():
    fighterName = request.form.get('fighterName') or None
    con = mysql.connection
    cur = con.cursor()
 
    # Query to generate the leaderboard, or the 3 Fighters with the most wins. 
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

    # Query to generate the win results for a single Fighter, filtered by name. 
    cur.execute('''SELECT Fighters.fighterName, IFNULL(SUM(Wins.WinCount), 0) as `Total` FROM 
		Fighters LEFT JOIN 
        (SELECT fighter1 as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1
        UNION 
         SELECT fighter2 as fighterID, COUNT(fightID) as WinCounts  FROM Fights WHERE fighter2Won GROUP BY fighter2) AS Wins
        
        ON Wins.fighterID = Fighters.fighterID
        WHERE Fighters.fighterName = %s
        GROUP BY Wins.fighterID;''', (fighterName,))
    individual = cur.fetchall()
       
    # Query to generate the prize results for a single Fighter, filtered by name. 
    cur.execute('''SELECT IFNULL(p.prizeType, 'No Prizes Won') as prizeType, f.fighterName
        FROM Fighters as f
        LEFT JOIN PrizesWon as pw ON f.fighterID=pw.fighterID
        LEFT JOIN Prizes as p 
        ON pw.prizeID=p.prizeID
        WHERE f.fighterName = %s;''', (fighterName,))
    prizesWon = cur.fetchall()
    
    return render_template('results.html', leaders=leaders, individual=individual, prizesWon=prizesWon)

      

# -------------------------------------------------------------------------------------------------
# Fights Page
@app.route('/fights')
def fightsetup(error=None):
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
    cur.execute('''SELECT fightID from Fights ORDER BY fightID asc;''')
    fightIDs = cur.fetchall()
    cur.execute('''SELECT fighterName, fighterID from Fighters ORDER BY fighterName asc;''')
    available_fighters=cur.fetchall()
    cur.execute('''SELECT prizeID, prizeType from Prizes;''')
    available_prizes=cur.fetchall()

    return render_template('fights.html', fights=fights, available_fighters=available_fighters, available_prizes=available_prizes, fightIDs=fightIDs, error=error)
    
@app.route('/fights', methods=['POST'])
def modify_fight():
    error=None
    print(request.form.to_dict())
    if request.form.get('fight-update'):
        con = mysql.connection
        cur = con.cursor()
        fightID = request.form.get('old-fight-id') 
        
        # If the fightDate and prizeWon weren't assigned, stay with the current values in the database.
        cur.execute('''SELECT fightDate FROM Fights WHERE fightID = %s;''', (fightID,))
        fightDate = request.form.get('new-fight-date') or cur.fetchone()['fightDate']
        
        cur.execute('''SELECT prize FROM Fights WHERE fightID = %s;''', (fightID,))
        prizeID = request.form.get('new-prize-id') or cur.fetchone()['prize']
        result = request.form.get('fight-winner') or None
        fighter1Won = 0
        fighter2Won = 0
        
        if result == 'fighter1-won': 
            fighter1Won = 1
            fighter2Won = 0
        elif result == 'fighter2-won': 
            fighter1Won = 0
            fighter2Won = 1
        print(fightID, fightDate, fighter1Won, fighter2Won, prizeID)
        try:
            cur.execute('''UPDATE Fights SET fightDate = %s, fighter1Won = %s, fighter2Won = %s, prize = %s WHERE fightID = %s;''', (fightDate, fighter1Won, fighter2Won, 
            prizeID, fightID))
            con.commit()
        
        except:
             print('Fight Update Failed')
        
    elif request.form.get('fight-insert'):
        fighter1 = request.form.get('fighter1-id') or None
        fighter2 = request.form.get('fighter2-id') or None
        
            
        prize = request.form.get('prize-id') or None
        fightDate = request.form.get('fight-date') or None
        # Fights require two distinct Fighters.
        if fighter1 == fighter2:
            error = 'Fights must be between two different Fighters. Try again.'
        if fightDate is None:
            error = 'Fight Date is a required field. Try again.'
     
        else:
            try:
                con = mysql.connection
                cur = con.cursor()
                cur.execute('''INSERT INTO Fights (fighter1, fighter2, prize, fightDate) 
                    VALUES (%s, %s, %s, %s);''', (fighter1, fighter2, prize, fightDate))
                con.commit()

            except:
                print('Insert Failed')
        
    elif request.form.get('fight-filter'):
        startDate = request.form.get('start-date') or None
        endDate = request.form.get('end-date') or None

        try:
            con = mysql.connection
            cur = con.cursor()
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
				AND (one.fightDate >= %s OR %s IS NULL)
                AND (one.fightDate <= %s OR %s IS NULL)
                ORDER BY one.fightDate desc;''', (startDate, startDate, endDate, endDate))
                
                
            fights = cur.fetchall()
            return render_template('fights.html', fights=fights, filtered=1)
        except:
            print('Fight Filter Failed')
    
    elif request.form.get('clear-fight-filter'):
        pass
    return fightsetup(error=error)

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
    cur.execute('''SELECT fighterName, fighterID from Fighters''')
    available_fighters=cur.fetchall()
    cur.execute('''SELECT prizeID, prizeType from Prizes''')
    available_prizes=cur.fetchall()
    
    return render_template('prizes.html', allPrizes=allPrizes, prizesWon=prizesWon, available_fighters=available_fighters, available_prizes=available_prizes)

@app.route('/prizes', methods=['POST'])
def modify_prize():
    print(request.form.to_dict())
    if request.form.get('new-prize'):
        prizeType = request.form.get('prize-type') or None 
        try:
            con = mysql.connection
            cur = con.cursor()
            cur.execute('''INSERT INTO Prizes (prizeType) VALUES(%s);''', (prizeType,))
            # Note to future reader: the trailing comma after the prizeType variable is absolutely required for Python to identify this as a tuple.
            con.commit()

        except:
            print("Prizes - Insert Failed")
    elif request.form.get('prize-won'):
        prizeID = request.form.get('prize-id') 
        fighterID = request.form.get('fighter-id') 
        try:
            con = mysql.connection
            
            cur = con.cursor()
            cur.execute('''INSERT INTO PrizesWon (fighterID, prizeID) VALUES (%s, %s);''', (fighterID, prizeID))
            con.commit()

        except:
            print("PrizesWon - Insert Failed")
    
    elif request.form.get('prize-won-delete'):
        print("Delete entered")
        prizeID = eval(request.form.get('prize-won-delete'))[0]
        fighterID = eval(request.form.get('prize-won-delete'))[1] 
        print(prizeID)
        print(fighterID)
        try:
            con = mysql.connection
            cur = con.cursor()
            cur.execute('''DELETE FROM PrizesWon WHERE fighterID=%s and prizeID=%s;''', (fighterID, prizeID))
            con.commit()

        except:
            print("PrizesWon - Delete Failed")
                    
    return prizes()
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 61557))
    app.run(port=port, debug=True)