from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
from datetime import datetime, date

organiser_bp = Blueprint('organiser', __name__, url_prefix='/organiser')

@organiser_bp.route('/portal', methods=['GET', 'POST'])
def organiser_portal():
    if session.get('role') not in ['Admin', 'organiser']:
        return redirect(url_for('main.home'))
        
    conn = get_db_connection()
    
    # If admin, fetch all events. If organiser, fetch only their events.
    if session.get('role') == 'Admin':
        events_query = 'SELECT * FROM events ORDER BY date ASC'
        events = conn.execute(events_query).fetchall()
    else:
        events_query = 'SELECT * FROM events WHERE created_by = ? ORDER BY date ASC'
        events = conn.execute(events_query, (session['user_id'],)).fetchall()
        
    # Query to fetch all interested users linked to events
    interests_query = '''
        SELECT 
            ei.event_id,
            u.first_name,
            u.last_name,
            u.username,
            u.email
        FROM event_interests ei
        JOIN users u ON ei.user_id = u.id
    '''
    interest_rows = conn.execute(interests_query).fetchall()
    conn.close()
    
    # Group interested users by event_id for easy lookup in the HTML
    interests_by_event = {}
    for row in interest_rows:
        e_id = row['event_id']
        if e_id not in interests_by_event:
            interests_by_event[e_id] = []
        interests_by_event[e_id].append({
            'name': f"{row['first_name']} {row['last_name']}",
            'username': row['username'],
            'email': row['email']
        })

    today_date = date.today().isoformat()
    return render_template(
        'organiser_portal.html', 
        today=today_date, 
        events=events, 
        interests_by_event=interests_by_event
    )

#########################################################################################################

@organiser_bp.route('/create-event', methods=['GET', 'POST'])
def create_event():
    if session.get('role') not in ['organiser', 'Admin']:
        return redirect(url_for('main.home'))
       
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_str = request.form['date']
        room = request.form['room']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        created_by = session['user_id']
        
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
        if selected_date < date.today():
            return "Error: You cannot create an event for a date in the past."
        
        if selected_date == date.today():
            current_time = datetime.now().time()
            event_start_time = datetime.strptime(start_time, '%H:%M').time()
            if event_start_time < current_time:
                return "Error: You cannot set an event start time that has already passed today."
            
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO events (title, description, date, start_time, end_time, room, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, date_str, start_time, end_time, room, created_by))
        conn.commit()
        conn.close()
        
    return redirect(url_for('organiser.organiser_portal'))

#########################################################################################################

@organiser_bp.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if session.get('role') not in ['Admin', 'organiser']:
        return redirect(url_for('main.home'))
        
    conn = get_db_connection()
    
    if session.get('role') == 'organiser':
        event = conn.execute('SELECT * FROM events WHERE id = ? AND created_by = ?', 
                             (event_id, session['user_id'])).fetchone()
        if not event:
            conn.close()
            return "Error: You do not have permission to delete this event."
    
    conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('organiser.organiser_portal'))