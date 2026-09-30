from flask import Blueprint, render_template, jsonify, session, Response, url_for

from database import get_db_connection

from datetime import date, timedelta


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

import datetime

@main_bp.route('/Events')
def events_page():
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events').fetchall()
    conn.close()
    
    # ADD datetime=datetime RIGHT HERE:
    return render_template('Events.html', events=events, year=year, month=month, datetime=datetime)

@main_bp.route('/Contact')
def contact():
    return render_template('Contact.html')

@main_bp.route('/About')
def about():
    return render_template('About.html')

@main_bp.route('/Gallery')
def gallery():
    return render_template('Gallery.html')

###########################################################################################

@main_bp.route('/api/interest/<int:event_id>', methods=['POST'])
def toggle_interest(event_id):
    # Ensure the user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in first.'}), 401

    user_id = session['user_id']
    conn = get_db_connection()
    
    # Check if the user is already interested in this event
    existing = conn.execute(
        'SELECT * FROM event_interests WHERE event_id = ? AND user_id = ?',
        (event_id, user_id)
    ).fetchone()

    if existing:
        # If already interested, remove it (toggle off)
        conn.execute(
            'DELETE FROM event_interests WHERE event_id = ? AND user_id = ?',
            (event_id, user_id)
        )
        is_interested = False
    else:
        # Otherwise, add it (toggle on)
        conn.execute(
            'INSERT INTO event_interests (event_id, user_id) VALUES (?, ?)',
            (event_id, user_id)
        )
        is_interested = True

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'is_interested': is_interested})




@main_bp.route('/event/<int:event_id>/ics')
def download_ics(event_id):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    conn.close()
    
    if not event:
        return "Event not found", 404

    # Format dates and times for iCalendar (e.g., '2026-10-23' -> '20261023')
    date_clean = event['date'].replace('-', '')
    start_clean = event['start_time'].replace(':', '') + '00'
    end_clean = event['end_time'].replace(':', '') + '00'
    
    dtstart = f"{date_clean}T{start_clean}"
    dtend = f"{date_clean}T{end_clean}"

    # Build the standard ICS file text format
    ics_content = f"""BEGIN:VCALENDAR
                        VERSION:2.0
                        PRODID:-//USS Event Website//NOCG//EN
                        BEGIN:VEVENT
                        UID:event-{event['id']}@usswebsite.local
                        DTSTAMP:{date_clean}T000000Z
                        DTSTART:{dtstart}
                        DTEND:{dtend}
                        SUMMARY:{event['title']}
                        DESCRIPTION:{event['description']}
                        LOCATION:{event['room']}
                        END:VEVENT
                        END:VCALENDAR"""

    return Response(
        ics_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=event_{event['id']}.ics"}
    )
    


@main_bp.route('/Student-Portal') # Or whatever your student route is named
def notifications():
    # Ensure user is logged in as a student
    if session.get('role') != 'Student':
        return redirect(url_for('main.home'))
        
    conn = get_db_connection()
    
    # Calculate today and 7 days from now
    today = date.today().isoformat()
    next_week = (date.today() + timedelta(days=7)).isoformat()
    
    # Fetch events happening within the next week
    upcoming_notifications = conn.execute('''
        SELECT * FROM events 
        WHERE date BETWEEN ? AND ? 
        ORDER BY date ASC, start_time ASC
    ''', (today, next_week)).fetchall()
    
    # Also fetch all regular events for your main display
    events = conn.execute('SELECT * FROM events ORDER BY date ASC').fetchall()
    
    conn.close()
    
    return render_template('student_dashboard.html', events=events, notifications=upcoming_notifications)