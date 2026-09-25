###################################################################################################################
                                                                                                                  #
###################################################################################################################

# ==========================================
# 1. Importation 
# ==========================================
#below are all the tools that are going to be used in the making of this app.py :)

import random #this is used for random number generation for generating a username
import sqlite3 #this is used for creating a db to store user details 
from flask import Flask, render_template, request, redirect, url_for, session #flask is used to talk between python and html
from werkzeug.security import generate_password_hash, check_password_hash #werkzueg security hashes your passwords so they are kept safe 

###################################################################################################################
                                                                                                                  #
###################################################################################################################

# ==========================================
# 2. APP CONFIGURATION & SETUP
# ==========================================

app = Flask(__name__, template_folder='templates/HTML') #directs flask to the right folder where the html is kept 
app.secret_key = 'your_unique_secret_key_here' # Required to secure user login sessions

###################################################################################################################
                                                                                                                  #
###################################################################################################################

# ==========================================
# 3. DATABASE HELPER FUNCTIONS
# ==========================================

def get_db_connection():
    conn = sqlite3.connect('uss_events.db') #conn now equals sql connecting to the db 
    conn.row_factory = sqlite3.Row
    return conn #conn is just a shorter way of saying connection 

def init_db():
    conn = get_db_connection() 
    # Creates the users table with role support if it doesn't already exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            dob TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
    )
    ''') #all of that section jusdt above is sql, makes it so the data cannot be null 
    conn.commit() #once the users are in the changes get committed 
    conn.close()

# Automatically build the database table when the server starts
init_db()

###################################################################################################################
                                                                                                                  #
###################################################################################################################

# ==========================================
# 4. STATIC PAGE ROUTES (Existing Pages)
# ==========================================

#The below section is taking the html files and turning them into something that python understands, 
#this is changing the html directories into python directories, below it will be shown why 

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/Student-Portal')
def studentportal():
    return render_template('Student-Portal.html')

@app.route('/Events')
def events():
    return render_template('Events.html')

@app.route('/Contact')
def contact():
    return render_template('Contact.html')

@app.route('/About')
def about():
    return render_template('About.html')

@app.route('/Gallery')
def gallery():
    return render_template('Gallery.html')


###################################################################################################################
                                                                                                                  #
###################################################################################################################

# ==========================================
# 5. AUTHENTICATION & USER ACCOUNT ROUTES
# ==========================================

#this is the same as the code above just with extra steps making the user acutally log in or sign up before they can access their profile.

@app.route('/Signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST': #post is used in html forms
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        email = request.form['email']
        password = request.form['password']
        
        # Automatically generate a university-style username 
        base_username = f"{first_name[0].lower()}{last_name.lower()[:5]}" #grabs first letter of first name and up to 5 letters of last name
        random_suffix = f"{random.randint(0, 99):02d}" #generates a random number that is 2 digits
        username = f"{base_username}{random_suffix}" #adds them together
        
        # Hash the password so it's secure in the database
        hashed_password = generate_password_hash(password)
        
        # Default new accounts to the pending 'user' role until permissions are granted
        role = 'user' 
        
        conn = get_db_connection() #this was already declared but cannot be called on again because it was in a def(), therefore it has to be redeclared 
        try:
            conn.execute('INSERT INTO users (first_name, last_name, username, email, dob, password, role) VALUES (?, ?, ?, ?, ?, ?, ?)', #execute method runs 
                         (first_name, last_name, username, email, dob, hashed_password, role))
            conn.commit() #commit method saves changes 
            conn.close() #close method closes 
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists (or username collision)! Go back and try another."
            
    return render_template('Sign up.html')

###################################################################################################################
                                                                                                                  #
###################################################################################################################


@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': #post is the method used in html forms, get is to view it
        username_or_email = request.form['username_or_email'] #gives the user a choice between username or email (not sure if ill keep this)
        password = request.form['password'] 
        
        conn = get_db_connection() #this was already declared but cannot be called on again because it was in a def(), therefore it has to be redeclared 
        # Look up the user by either their username or email
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', #execute runs the sql query, * means ALL, ? makes it so only text is accepetd and hackers cannot inject code 
                            (username_or_email, username_or_email)).fetchone() #fetchone tells the database to give me the first result that matches the input
        conn.close()
        
        # Check if user exists and verify the hashed password matches
        if user and check_password_hash(user['password'], password): #checks if the user exists, if there was no email/username then user = none 
            # Store their info in Flask's secure session cookie      if user does exist it goes to the next line of code, check_password_hash checks 
            session['user_id'] = user['id']                          #the password that was just typed and scrambles it and sees if it matches with the db
            session['username'] = user['username']
            session['role'] = user['role']
            session['first_name'] = user['first_name']  
            session['last_name'] = user['last_name']    
            
            # Send them to a placeholder dashboard (we can build this next!)
            return redirect(url_for('profile'))
        else:
            return "Invalid username/email or password. Go back and try again."
            
    return render_template('Log in.html')

###################################################################################################################
                                                                                                                  #
###################################################################################################################

#profile section 

@app.route('/Profile')
def profile():
    # Check if the user is actually logged in via session
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('Profile.html')

###################################################################################################################
                                                                                                                  #
###################################################################################################################

@app.route('/logout')
def logout():
    session.clear() # Wipe the user session data
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

