from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
from datetime import date


organiser_bp = Blueprint('organiser', __name__, url_prefix='/organiser')


@organiser_bp.route('/portal', methods=['GET', 'POST'])
def organiser_portal():
    if session.get('role') not in ['organiser']:
        return redirect(url_for('main.home'))

    # Get today's date in YYYY-MM-DD format
    today_date = date.today().isoformat()

    # Handle form submission for creating events here...
    return render_template('organiser_portal.html')


@organiser_bp.route('/create-event', methods=['GET', 'POST'])
def create_event():
    # Security check: Only Admins and Organisers can create events
    if session.get('role') not in ['organiser']:
        return redirect(url_for('main.home'))
       
    from datetime import datetime

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_str = request.form['date'] # format will be 'YYYY-MM-DD'
        room = request.form['room']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        created_by = session['user_id']
        
        # Check if the submitted date is in the past
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if selected_date < date.today():
            return "Error: You cannot create an event for a date in the past."
            
        # Proceed with database insertion if the date is valid...
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO events (title, description, date, start_time, end_time, room, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, date_str, start_time, end_time, room, created_by))
        conn.commit()
        conn.close()
        
        return redirect(url_for('organiser.organiser_portal'))

