import random
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

# Create a blueprint for authentication and user accounts
auth_bp = Blueprint('auth', __name__)










#####################################################################################################################################

#####################################################################################################################################









@auth_bp.route('/Signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('auth.profile'))
    
    if request.method == 'POST': # post is used in html forms
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        email = request.form['email']
        password = request.form['password']
        
        # Automatically generate a university-style username 
        base_username = f"{first_name[0].lower()}{last_name.lower()[:5]}" # grabs first letter of first name and up to 5 letters of last name
        random_suffix = f"{random.randint(0, 99):02d}" # generates a random number that is 2 digits
        username = f"{base_username}{random_suffix}" # adds them together
        
        # Hash the password so it's secure in the database (werkzeug security)
        hashed_password = generate_password_hash(password)
        
        # Default new accounts to user
        role = 'user' 
        
        conn = get_db_connection() # this was already declared but cannot be called on again because it was in a def(), therefore it has to be redeclared 
        try:
            conn.execute('INSERT INTO users (first_name, last_name, username, email, dob, password, role) VALUES (?, ?, ?, ?, ?, ?, ?)', # execute method runs 
                         (first_name, last_name, username, email, dob, hashed_password, role))
            conn.commit() # commit method saves changes 
            conn.close() # close method closes 
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists (or username collision)! Go back and try another."
            
    return render_template('Sign up.html')

#####################################################################################################################################

@auth_bp.route('/Login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: #if user is logged in 
        return redirect(url_for('auth.profile')) #redirect to profile page 
    
    if request.method == 'POST': # post is the method used in html forms, get is to view it, if request = post
        username_or_email = request.form['username_or_email'] # gives the user a choice between username or email
        password = request.form['password']  #enter password
        
        conn = get_db_connection() # this was already declared but cannot be called on again because it was in a def(), therefore it has to be redeclared 
        # Look up the user by either their username or email
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', # execute runs the sql query, * means ALL, ? makes it so only text is accepted and hackers cannot inject code 
                            (username_or_email, username_or_email)).fetchone() # fetchone tells the database to give me the first result that matches the input
        conn.close()
        
        # Check if user exists and verify the hashed password matches
        if user and check_password_hash(user['password'], password): # checks if the user exists, if there was no email/username then user = none 
            # Store their info in Flask's secure session cookie 
            session['user_id'] = user['id'] 
            session['role'] = user['role']
            return redirect(url_for('auth.profile'))
        else:
            return "Invalid username/email or password. Go back and try again."
            
    return render_template('Log in.html')













#####################################################################################################################################

#####################################################################################################################################









@auth_bp.route('/Profile')
def profile():
    # Check if the user is an Admin, redirect to dashboard
    if session.get('role') == 'Admin': #if role = admin 
        return redirect(url_for('admin.dashboard')) #redirect to dashboard
    
    if session.get('role') =='organiser': #if role = organsier
        return redirect(url_for('organiser.organiser_portal')) #redirect to portal
    
    # Check if the user is actually logged in via session
    if 'user_id' not in session: #if user not logged in
        return redirect(url_for('auth.login')) #redirect to login
    
    # Fetch user data from database using their session ID
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    # Pass the 'user' object into the HTML template!
    return render_template('Profile.html', user=user)

#####################################################################################################################################









#####################################################################################################################################

#####################################################################################################################################









# Automatically makes 'user' available in the navbar for all Jinja templates
@auth_bp.app_context_processor
def inject_user():
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        return dict(user=user)
    return dict(user=None)








#####################################################################################################################################

#####################################################################################################################################






@auth_bp.route('/logout')
def logout():
    session.clear() # Wipe the user session data
    return redirect(url_for('main.home'))