from flask import Flask, render_template

# Point Flask to your templates folder
app = Flask(__name__, template_folder='templates/HTML')

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/Student-Portal')
def studentportal():
    return render_template('Student-Portal.html')

@app.route('/Events')
def events():
    return render_template('Events.html')

@app.route('/Login')
def login():
    return render_template('Log in.html')

@app.route('/Signup')
def signup():
    return render_template('Sign up.html')

@app.route('/Profile')
def profile():
    return render_template('Profile.html')

@app.route('/Contact')
def contact():
    return render_template('Contact.html')

@app.route('/About')
def about():
    return render_template('About.html')

@app.route('/Gallery')
def gallery():
    return render_template('Gallery.html')

if __name__ == '__main__':
    app.run(debug=True)