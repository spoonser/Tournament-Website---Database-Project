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
    
@app.route('/weapons')
def weapons():
    return render_template('weapons.html')
    
@app.route('/results')
def results():
    return render_template('results.html')
      
@app.route('/fights')
def fights():
    return render_template('fights.html')

	
if __name__ == '__main__':
    app.run(host="localhost", port=61557, debug=True)