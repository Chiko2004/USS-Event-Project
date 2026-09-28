#####################################################################################################################################
#admin routes are specifically for handling routes that are only accessable by admins 

from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

#flask is for speaking to html with python logic, hosts its own server ect
#blueprint to break up python files from "app.py" for readability, render template loads html pages, request grabs data, redirect is redirect, url for is directory and session is cookies 

#####################################################################################################################################

# Creates an admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users')
def manage_users():
    # Security check: Make sure someone is logged in AND is an Admin
    if session.get('role') != 'Admin':
        return redirect(url_for('main.home'))
    
    # Fetch all users from the database
    conn = get_db_connection()
    all_users = conn.execute('SELECT id, first_name, last_name, username, email, role FROM users').fetchall()
    conn.close()
    
    return render_template('Dashboard.html', all_users=all_users)

#####################################################################################################################################

# Route for an admin to update any user's details directly from the dashboard table
# Change the route path to just '/update-user/<int:user_id>' because of the blueprint prefix


@admin_bp.route('/update-user/<int:user_id>', methods=['POST'])
def edit_user_inline(user_id): # Match the name expected by your HTML url_for()
    if session.get('role') != 'Admin':
        return redirect(url_for('main.home'))
    
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    role = request.form['role']
    new_password = request.form['password']
    
    conn = get_db_connection()
    try:
        if new_password.strip():
            hashed_password = generate_password_hash(new_password)
            conn.execute('''
                UPDATE users 
                SET first_name = ?, last_name = ?, email = ?, password = ?, role = ? 
                WHERE id = ?
            ''', (first_name, last_name, email, hashed_password, role, user_id))
        else:
            conn.execute('''
                UPDATE users 
                SET first_name = ?, last_name = ?, email = ?, role = ? 
                WHERE id = ?
            ''', (first_name, last_name, email, role, user_id))
            
        conn.commit()
        conn.close()
        return redirect(url_for('admin.manage_users'))
        
    except sqlite3.IntegrityError:
        conn.close()
        return "That email address is already taken by another account."