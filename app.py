from flask import Flask
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
    # Placeholder -- will allow creation/modification of fighters (change weapon, change name)
    # Fighter profiles will link to that fighter's prize results
    
@app.route('/weapons')
def weapons():
    return render_template('weapons.html')
    # placeholder -- will allow creation/modification of weapons, links to fighter using that weapon (if any)
    # TBD - might also allow a general search by weapon type, general search for all fighters using that weapon type
    
@app.route('/results')
def results():
    return render_template('results.html')
    # placeholder -- will contain leaderboard (fighters with most wins) and per-fighter prize lookup
   
@app.route('/fights')
def fights():
    return render_template('fights.html')
    # placeholder -- will allow creation/modification of fights (who is participating, when it is)
    # TBD - could also do the prizes-to-fights assignment and winner assignment here. 
    
@app.route('/test')
def hello_world():
    return 'Hello, World!'
	
if __name__ == '__main__':
    app.run(host="localhost", port=61557, debug=True)