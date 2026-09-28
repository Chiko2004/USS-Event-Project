from flask import Blueprint, render_template
from database import get_db_connection

# Create a blueprint for general pages
main_bp = Blueprint('main', __name__)

# The below section is taking the html files and turning them into something that python understands, 
# this is changing the html directories into python directories

@main_bp.route('/')
def home():
    return render_template('Home.html')

@main_bp.route('/Student-Portal')
def studentportal():
    return render_template('Student-Portal.html')

@main_bp.route('/events')
def events_page():
    conn = get_db_connection()
    # Fetch all events from your database table
    events = conn.execute('SELECT * FROM events').fetchall()
    conn.close()
    
    return render_template('events.html', events=events)

@main_bp.route('/Contact')
def contact():
    return render_template('Contact.html')

@main_bp.route('/About')
def about():
    return render_template('About.html')

@main_bp.route('/Gallery')
def gallery():
    return render_template('Gallery.html')