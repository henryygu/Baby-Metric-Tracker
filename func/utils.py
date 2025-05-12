import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import time
import plotly.express as px

@st.cache_resource
def init_db():
    conn = sqlite3.connect("baby_log.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            details TEXT,
            timestamp TIMESTAMP,
            comments TEXT,
            End_timestamp TIMESTAMP,
            orientation TEXT
        )
    """)
    conn.commit()
    return conn

conn = init_db()

def get_bst_time():
    bst_tz = pytz.timezone('Europe/London')
    return datetime.now(bst_tz)

def log_event(event, details="", End_timestamp="", orientation="", comments = ""):
    c = conn.cursor()
    bst_time = get_bst_time().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("""
        INSERT INTO logs (event, details, timestamp, End_timestamp, orientation, comments) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (event, details, bst_time, End_timestamp, orientation, comments))
    conn.commit()

def update_event(event_id, new_details):
    c = conn.cursor()
    c.execute("""
        UPDATE logs 
        SET details = ? 
        WHERE id = ?
    """, (new_details, event_id))
    conn.commit()

def get_last_feed(ongoing=True, orientation=""):
    c = conn.cursor()
    
    if ongoing:
        # Get last ongoing feed
        query = """
            SELECT id, timestamp 
            FROM logs 
            WHERE event = 'Feeding' AND details = 'ongoing'
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        c.execute(query)
    else:
        # Get last completed feed, optionally filtered by orientation
        query = """
            SELECT timestamp, details, orientation
            FROM logs 
            WHERE event = 'Feeding' AND details != 'ongoing'
        """
        params = ()
        
        if orientation:
            query += " AND orientation = ?"
            params = (orientation,)
            
        query += " ORDER BY timestamp DESC LIMIT 1"
        c.execute(query, params)
    
    return c.fetchone()
def get_last_diaper_change():
    c = conn.cursor()
    c.execute("""
        SELECT event, timestamp 
        FROM logs 
        WHERE event IN ('Pee', 'Poop', 'Mixed') 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    result = c.fetchone()
    return result if result else (None, None)

def get_diaper_counts(start_datetime=None, end_datetime=None):
    c = conn.cursor()
    
    # Initialize counts
    counts = {'Pee': 0, 'Poop': 0, 'Mixed': 0}
    
    # Build query based on parameters
    query = """
        SELECT event, COUNT(*) as count 
        FROM logs 
        WHERE event IN ('Pee', 'Poop', 'Mixed')
    """
    params = []
    
    if start_datetime is not None and end_datetime is not None:
        query += " AND timestamp BETWEEN ? AND ?"
        params.extend([start_datetime.strftime('%Y-%m-%d %H:%M:%S'), 
                      end_datetime.strftime('%Y-%m-%d %H:%M:%S')])
    elif start_datetime is not None:
        query += " AND timestamp >= ?"
        params.append(start_datetime.strftime('%Y-%m-%d %H:%M:%S'))
    elif end_datetime is not None:
        query += " AND timestamp <= ?"
        params.append(end_datetime.strftime('%Y-%m-%d %H:%M:%S'))
    else:
        # Default to today's date if no time window specified
        query += " AND date(timestamp) = date(?)"
        params.append(get_bst_time().strftime('%Y-%m-%d'))
    
    query += " GROUP BY event"
    
    c.execute(query, params)
    results = c.fetchall()
    
    for event, count in results:
        counts[event] = count
    
    return counts

def format_timedelta(delta):
    if delta is None:
        return "Never"
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_all_diaper_data(days=7):
    c = conn.cursor()
    cutoff_date = (get_bst_time() - timedelta(days=days)).strftime('%Y-%m-%d')
    c.execute("""
        SELECT date(timestamp) as date, event, COUNT(*) as count 
        FROM logs 
        WHERE event IN ('Pee', 'Poop', 'Mixed')
        AND date(timestamp) >= date(?)
        GROUP BY date(timestamp), event
        ORDER BY date(timestamp)
    """, (cutoff_date,))
    return c.fetchall()

def get_all_weight_data(days=7):
    c = conn.cursor()
    cutoff_date = (get_bst_time() - timedelta(days=days)).strftime('%Y-%m-%d')
    c.execute("""
        SELECT date(timestamp) as date, event, Comments as Weight 
        FROM logs 
        WHERE event IN ('Other')
        and details = 'Weight'
        AND date(timestamp) >= date(?)
        ORDER BY date(timestamp)
    """, (cutoff_date,))
    return c.fetchall()

def get_all_diaper_time_data(days=7):
    c = conn.cursor()
    cutoff_date = (get_bst_time() - timedelta(days=days)).strftime('%Y-%m-%d')
    c.execute("""
        SELECT timestamp as date, event, COUNT(*) as count 
        FROM logs 
        WHERE event IN ('Pee', 'Poop', 'Mixed')
        AND timestamp >= (?)
        GROUP BY timestamp, event
        ORDER BY timestamp
    """, (cutoff_date,))
    return c.fetchall()

def get_all_feeding_data(days=7):
    c = conn.cursor()
    cutoff_date = (get_bst_time() - timedelta(days=days)).strftime('%Y-%m-%d')
    c.execute("""
        SELECT timestamp, details 
        FROM logs 
        WHERE event = 'Feeding' AND details != 'ongoing'
        AND date(timestamp) >= date(?)
        ORDER BY timestamp
    """, (cutoff_date,))
    feeding_data = c.fetchall()
    if feeding_data:
        # Process feeding durations
        feeding_records = []
        for timestamp, duration in feeding_data:
            time_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            date = time_obj.date()
            
            # Parse duration (format: HH:MM:SS)
            h, m, s = map(int, duration.split(':'))
            duration_min = h * 60 + m + s / 60
            
            feeding_records.append({
                'Date': date,
                'Time': time_obj.time(),
                'Duration (min)': duration_min,
                'Timestamp': timestamp
            })
        
    return pd.DataFrame(feeding_records)

def format_time_short(delta):
    if delta is None:
        return "Never"
    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "<1m"

def get_time_since_last(event_type):
    c = conn.cursor()
    c.execute("""
        SELECT timestamp 
        FROM logs 
        WHERE event = ?
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (event_type,))
    result = c.fetchone()
    if result:
        last_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        last_time = pytz.timezone('Europe/London').localize(last_time)
        return get_bst_time() - last_time
    return None

def get_last_diaper_any():
    c = conn.cursor()
    c.execute("""
        SELECT event, timestamp 
        FROM logs 
        WHERE event IN ('Pee', 'Poop', 'Mixed')
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    result = c.fetchone()
    if result:
        event, timestamp = result
        last_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        last_time = pytz.timezone('Europe/London').localize(last_time)
        time_since = get_bst_time() - last_time
        return event, format_time_short(time_since), timestamp
    return None, "Never", None

def format_age(birth_date):
    today = datetime.now().date()
    total_days = (today - birth_date).days
    delta = relativedelta(today, birth_date)
    
    # Build the breakdown parts
    parts = []
    if delta.years > 0:
        parts.append(f"{delta.years} year{'s' if delta.years != 1 else ''}")
    if delta.months > 0:
        parts.append(f"{delta.months} month{'s' if delta.months != 1 else ''}")
    if delta.days > 0 or not parts:  # Always show days if nothing else
        parts.append(f"{delta.days} day{'s' if delta.days != 1 else ''}")
    
    # Join the parts with correct punctuation
    if len(parts) > 1:
        breakdown = ', '.join(parts[:-1]) + ' and ' + parts[-1]
    else:
        breakdown = parts[0] if parts else "0 days"
    
    return total_days, breakdown



@st.fragment(run_every="1s")
def update_feed_info():
    last_feed = get_last_feed()
    current_bst = get_bst_time()
    
    if last_feed:
        feed_id, start_time = last_feed
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        start_time = pytz.timezone('Europe/London').localize(start_time)
        duration = current_bst - start_time
        
        st.write(f"Feed started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"Duration so far: {format_timedelta(duration)}")
@st.fragment(run_every="1s")
def update_last_feed():
    current_bst = get_bst_time()
    last_time_all, duration_all, orientation_all = get_last_feed(ongoing=False)
    last_time_1 = datetime.strptime(last_time_all, '%Y-%m-%d %H:%M:%S')
    last_time_1 = pytz.timezone('Europe/London').localize(last_time_1)
    time_since = current_bst - last_time_1
    st.write(f"Last orientation: {orientation_all}")
    st.write(f"Duration: {duration_all}")
    st.write(f"Time since: {format_timedelta(time_since)}")
    
@st.fragment(run_every="1s")
def update_last_completed(type):
    current_bst = get_bst_time()
    last_time, duration, orientation = type
    last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
    last_time = pytz.timezone('Europe/London').localize(last_time)
    time_since = current_bst - last_time
    st.write(f"Duration: {duration}")
    st.write(f"Time since: {format_timedelta(time_since)}")