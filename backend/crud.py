from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from .models import Log
from .schemas import LogCreate
from datetime import datetime, timedelta
import pytz
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

TIMEZONE = config.get('timezone', 'Europe/London')
tz = pytz.timezone(TIMEZONE)

def get_current_time():
    return datetime.now(tz)

def log_event(db: Session, log: LogCreate):
    db_log = Log(**log.dict())
    if not db_log.timestamp:
        db_log.timestamp = get_current_time()
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs(db: Session, skip: int = 0, limit: int = 100, event: str = None):
    query = db.query(Log)
    if event:
        query = query.filter(Log.event == event)
    return query.order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()

def stop_ongoing_session(db: Session, event_type: str):
    ongoing = db.query(Log).filter(
        and_(Log.event == event_type, Log.details == "ongoing")
    ).order_by(Log.timestamp.desc()).first()
    
    if ongoing:
        end_time = get_current_time()
        start_time = ongoing.timestamp
        if start_time.tzinfo is None:
            start_time = tz.localize(start_time)
            
        duration = end_time - start_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        ongoing.details = duration_str
        ongoing.end_timestamp = end_time
        db.commit()
        db.refresh(ongoing)
    return ongoing

def get_stats(db: Session):
    now = get_current_time()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    
    # Feeding stats
    def get_feed_metrics(start, end=None):
        query = db.query(Log).filter(and_(Log.event == "Feeding", Log.details != "ongoing", Log.timestamp >= start))
        if end:
            query = query.filter(Log.timestamp < end)
        feeds = query.all()
        
        count = len(feeds)
        total_minutes = 0
        for f in feeds:
            if f.details and ":" in f.details:
                parts = list(map(int, f.details.split(':')))
                total_minutes += parts[0]*60 + parts[1] + parts[2]/60
        
        avg = total_minutes / count if count > 0 else 0
        return count, total_minutes, avg

    t_count, t_dur, t_avg = get_feed_metrics(today_start)
    y_count, y_dur, y_avg = get_feed_metrics(yesterday_start, today_start)
    
    feeding_stats = {
        "today_count": t_count,
        "today_duration": round(t_dur, 1),
        "today_avg": round(t_avg, 1),
        "yesterday_count": y_count,
        "yesterday_duration": round(y_dur, 1),
        "yesterday_avg": round(y_avg, 1),
        "count_delta": t_count - y_count,
        "duration_delta": round(t_dur - y_dur, 1),
        "avg_delta": round(t_avg - y_avg, 1)
    }
    
    # Diaper stats
    def get_diaper_count(event_type, start, end=None):
        query = db.query(Log).filter(and_(Log.event == event_type, Log.timestamp >= start))
        if end:
            query = query.filter(Log.timestamp < end)
        return query.count()

    diaper_types = ["Pee", "Poop", "Mixed"]
    diapers = {}
    for dt in diaper_types:
        tc = get_diaper_count(dt, today_start)
        yc = get_diaper_count(dt, yesterday_start, today_start)
        diapers[dt.lower()] = {"today_count": tc, "yesterday_count": yc, "delta": tc - yc}
    
    # Total diapers
    t_total = sum(d["today_count"] for d in diapers.values())
    y_total = sum(d["yesterday_count"] for d in diapers.values())
    diapers["total"] = {"today_count": t_total, "yesterday_count": y_total, "delta": t_total - y_total}
    
    # Last diaper
    last_diaper = db.query(Log).filter(Log.event.in_(diaper_types)).order_by(Log.timestamp.desc()).first()
    
    def get_last_str(event_types):
        l = db.query(Log).filter(Log.event.in_(event_types)).order_by(Log.timestamp.desc()).first()
        if not l: return "Never"
        lt = l.timestamp
        if lt.tzinfo is None: lt = tz.localize(lt)
        diff = now - lt
        h, rem = divmod(int(diff.total_seconds()), 3600)
        m = rem // 60
        return f"{h}h {m}m" if h > 0 else f"{m}m"

    if last_diaper:
        diapers["last_type"] = last_diaper.event
        diapers["last_time_str"] = get_last_str(diaper_types)
    else:
        diapers["last_type"] = None
        diapers["last_time_str"] = "Never"
    
    diapers["last_pee_str"] = get_last_str(["Pee", "Mixed"])
    diapers["last_poop_str"] = get_last_str(["Poop", "Mixed"])

    # Fetch last 7 days of logs for history/predictions
    seven_days_ago = today_start - timedelta(days=7)
    past_logs = db.query(Log).filter(Log.timestamp >= seven_days_ago).all()

    # History (7 days)
    history = {
        "feeding": [],
        "diaper": [],
        "sleep": [],
        "growth": []
    }
    
    for i in range(7):
        day_date = (today_start - timedelta(days=i)).replace(tzinfo=None)
        day_end = day_date + timedelta(days=1)
        day_str = day_date.strftime("%Y-%m-%d")
        
        # Feeding Day
        day_feeds = [l for l in past_logs if l.event == "Feeding" and day_date <= l.timestamp.replace(tzinfo=None) < day_end]
        orientations = {"Left": 0, "Right": 0, "Expressed": 0}
        for f in day_feeds:
            if f.orientation in orientations:
                orientations[f.orientation] += 1
        
        history["feeding"].append({
            "date": day_str,
            "count": len(day_feeds),
            "details": orientations
        })
        
        # Diaper Day
        day_diapers = [l for l in past_logs if l.event in diaper_types and day_date <= l.timestamp.replace(tzinfo=None) < day_end]
        d_types = {"Pee": 0, "Poop": 0, "Mixed": 0}
        for d in day_diapers:
            if d.event in d_types:
                d_types[d.event] += 1
        
        history["diaper"].append({
            "date": day_str,
            "count": len(day_diapers),
            "details": d_types
        })
        
        # Sleep Day Total
        day_sleeps = [l for l in past_logs if l.event == "Sleep" and l.details != "ongoing" and day_date <= l.timestamp.replace(tzinfo=None) < day_end]
        total_sleep_min = 0
        for s in day_sleeps:
            if s.timestamp and s.end_timestamp:
                dur = (s.end_timestamp.replace(tzinfo=None) - s.timestamp.replace(tzinfo=None)).total_seconds() / 60
                total_sleep_min += dur
        
        history["sleep"].append({
            "date": day_str,
            "total_hours": round(total_sleep_min / 60, 1)
        })
        
        # Growth Day
        day_growth = [l for l in past_logs if l.event == "Growth" and day_date <= l.timestamp.replace(tzinfo=None) < day_end]
        if day_growth:
            # Take the last one of the day
            g = day_growth[-1]
            history["growth"].append({
                "date": day_str,
                "weight": g.weight,
                "height": g.height
            })

    # Sleep predictions (14 days)
    sleep_logs = [l for l in past_logs if l.event == "Sleep" and l.details != "ongoing"]
    sleep_data = []
    for s in sleep_logs:
        st = s.timestamp
        if st.tzinfo is None: st = tz.localize(st)
        et = s.end_timestamp
        if et and et.tzinfo is None: et = tz.localize(et)
        if et:
            sleep_data.append({
                "date": st.strftime("%Y-%m-%d"),
                "start": st.strftime("%H:%M"),
                "end": et.strftime("%H:%M"),
                "is_predicted": False,
                "duration": (et - st).total_seconds() / 60
            })

    # Sleep predictions based on age and history
    # Age calculation
    val_dob = config['user']['date_of_birth']
    if isinstance(val_dob, str):
        dob = datetime.strptime(val_dob, "%Y-%m-%d").date()
    else:
        dob = val_dob # Assumed to be date or datetime
    if hasattr(dob, 'date'): dob = dob.date()
    age_months = (now.date().year - dob.year) * 12 + now.date().month - dob.month
    if now.date().day < dob.day: age_months -= 1

    # Developmental Norms
    # Simplified stages
    if age_months < 3:
        stage = "Newborn"
        norm_total = 14.0 # Avg
        norm_naps = 4
        # Small frequent sleeps
        base_norms = [
            {"start": "09:00", "end": "11:00"},
            {"start": "13:00", "end": "15:00"},
            {"start": "17:00", "end": "18:30"},
            {"start": "20:00", "end": "07:00"}
        ]
    elif age_months < 6:
        stage = "3-6 Months"
        norm_total = 13.0
        norm_naps = 3
        base_norms = [
            {"start": "09:30", "end": "11:00"},
            {"start": "13:30", "end": "15:30"},
            {"start": "19:30", "end": "07:00"}
        ]
    else:
        stage = "6-12 Months"
        norm_total = 12.0
        norm_naps = 2
        base_norms = [
            {"start": "09:30", "end": "11:00"},
            {"start": "14:00", "end": "16:00"},
            {"start": "19:00", "end": "07:00"}
        ]

    # Combine history + norms
    slots = []
    for s in sleep_logs:
        st = s.timestamp
        et = s.end_timestamp
        if not et: continue
        
        # Ensure we compare naive datetimes if SQLite stores them as such
        if st.tzinfo: st = st.replace(tzinfo=None)
        if et.tzinfo: et = et.replace(tzinfo=None)
        
        sm = st.hour * 60 + st.minute
        em = et.hour * 60 + et.minute
        if em < sm: em += 1440
        slots.append((sm, em))

    base_windows = []
    if slots:
        slots.sort()
        clusters = []
        curr = [slots[0]]
        for i in range(1, len(slots)):
            if slots[i][0] - curr[-1][0] < 120: 
                curr.append(slots[i])
            else:
                clusters.append(curr)
                curr = [slots[i]]
        clusters.append(curr)
        
        for c in clusters:
            if len(c) >= 2:
                avg_s = sum(x[0] for x in c) / len(c)
                avg_e = sum(x[1] for x in c) / len(c)
                hs, ms = divmod(int(avg_s) % 1440, 60)
                he, me = divmod(int(avg_e) % 1440, 60)
                base_windows.append({"start": f"{hs:02d}:{ms:02d}", "end": f"{he:02d}:{me:02d}"})

    # If history is sparse, use norms
    if not base_windows or len(base_windows) < 2:
        base_windows = base_norms

    # Sort base windows by start time for summary
    base_windows.sort(key=lambda x: x["start"])
    
    # Calculate durations for metadata
    prediction_details = []
    total_min = 0
    nap_count = 0
    for w in base_windows:
        hs, ms = map(int, w["start"].split(':'))
        he, me = map(int, w["end"].split(':'))
        sm = hs * 60 + ms
        em = he * 60 + me
        if em < sm: em += 1440
        dur = em - sm
        total_min += dur
        is_nap = dur < 300 # Rough heuristic: > 5 hours is night sleep
        if is_nap: nap_count += 1
        
        prediction_details.append({
            "start": w["start"],
            "end": w["end"],
            "duration": round(dur / 60, 1),
            "type": "Nap" if is_nap else "Night"
        })

    next_7_days = []
    for i in range(1, 15): # 14 day view as requested earlier
        future_date = (now + timedelta(days=i)).strftime("%Y-%m-%d")
        for w in base_windows:
            next_7_days.append({
                "date": future_date,
                "start": w["start"],
                "end": w["end"],
                "is_predicted": True
            })

    predictions = {
        "sleep": {
            "past": sleep_data,
            "future": next_7_days,
            "summary": {
                "stage": stage,
                "nap_count": nap_count,
                "total_hours": round(total_min / 60, 1),
                "details": prediction_details
            }
        }
    }

    # Ongoing
    ongoing_feed = db.query(Log).filter(and_(Log.event == "Feeding", Log.details == "ongoing")).order_by(Log.timestamp.desc()).first()
    ongoing_sleep = db.query(Log).filter(and_(Log.event == "Sleep", Log.details == "ongoing")).order_by(Log.timestamp.desc()).first()
    last_completed_feed = db.query(Log).filter(and_(Log.event == "Feeding", Log.details != "ongoing")).order_by(Log.timestamp.desc()).first()
    
    return {
        "feeding": feeding_stats,
        "diapers": diapers,
        "ongoing_feed": ongoing_feed,
        "ongoing_sleep": ongoing_sleep,
        "last_completed_feed": last_completed_feed,
        "predictions": predictions,
        "history": history
    }

def delete_log(db: Session, log_id: int):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log:
        db.delete(log)
        db.commit()
    return log

def get_latest_feed_id(db: Session):
    result = db.query(func.max(Log.feed_id)).filter(Log.event == "Feeding").first()
    return result[0] if result[0] is not None else 0
