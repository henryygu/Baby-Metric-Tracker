import time
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import yaml
import plotly.express as px

from func.utils import (
    df_to_dict,
    format_age,
    format_as_datetime,
    format_time_short,
    format_timedelta,
    get_data,
    get_last_diaper_change,
    get_last_feed,
    get_time,
    get_time_since_last,
    init_db,
    log_event,
    time_to_date,
    update_event,
    string_to_datetime,
    last_diaper,
    update_last_feed,
    update_feed,
    update_last_completed,
    update_feed_info,
    timeseries_datetime,
    get_feed_ids,
    create_new_feed_id, 
    latest_feed_id,
    get_all_weight_data,
    get_min_date
)

#####################################
# Load Configuration
#####################################
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    
dob = config["user"]["date_of_birth"]
name = config["user"]["name"]

conn = init_db()

st.header(f"👶 Baby Metric Tracker for {name}")
total_days, breakdown = format_age(dob)


st.write(f"It's been {breakdown} since {name} was born! or {total_days} days")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Tracker", "Diaper Viz", "Feeding Viz", "Weight Viz", "Logs"])






with tab1:
    if st.button("Refresh"):
        st.rerun()
    st.header("🍼 Feeding")  # This is the centered column
    last_feed = get_last_feed(ongoing=True)
    last_completed_feed_right = get_last_feed(ongoing=False, orientation="Right")
    last_completed_feed_left = get_last_feed(ongoing=False, orientation="Left")
    last_completed_feed_expressed = get_last_feed(ongoing=False, orientation="Expressed")
    if last_feed:
        last_feed = get_last_feed()
        update_feed_info(last_feed=last_feed)
        
    # Feeding Section
    update_last_feed()
    cola1, cola2 = st.columns(2)
            
    # Retrieve the latest feed IDs or create a new one
    feed_ids = get_feed_ids()
    with cola1:
        feed_id = st.selectbox("Select Feed ID", options= ["New Feed"] + feed_ids, index=0)
    with cola2:
        show_continue = st.toggle("Show Continue Feed Buttons", value=False)
    if feed_id == "New Feed":
        feed_id = create_new_feed_id()


   
    col1, col2, col3 = st.columns(3)

    with col1:
        if show_continue:
            if st.button("↩  Continue Feed Left"):
                log_event("Feeding", "ongoing", orientation="Left", feed_id=latest_feed_id())
        elif not last_feed:
            if st.button("⏺ Start Feed Left"):
                log_event("Feeding", "ongoing", orientation="Left", feed_id=feed_id)
        elif last_feed:
            if st.button("↩  Continue Feed Left"):
                update_feed(last_feed)
                log_event("Feeding", "ongoing", orientation="Left", feed_id=latest_feed_id())
    with col2:
        if show_continue:
            if st.button("↩  Continue Feed Right"):
                log_event("Feeding", "ongoing", orientation="Right", feed_id=latest_feed_id())
        elif not last_feed:
            if st.button("⏺ Start Feed Right"):
                log_event("Feeding", "ongoing", orientation="Right", feed_id=feed_id)
        elif last_feed:
            if st.button("↩  Continue Feed Right"):
                update_feed(last_feed)
                log_event("Feeding", "ongoing", orientation="Right", feed_id=latest_feed_id())
    with col3:
        if show_continue:
            if st.button("↩  Continue Feed Expressed"):
                log_event("Feeding", "ongoing", orientation="Expressed", feed_id=latest_feed_id())
        elif not last_feed:
            if st.button("⏺ Start Feed Expressed"):
                log_event("Feeding", "ongoing", orientation="Expressed", feed_id=feed_id)
        elif last_feed:
            if st.button("↩  Continue Feed Expressed"):
                update_feed(last_feed)
                log_event("Feeding", "ongoing", orientation="Expressed", feed_id=latest_feed_id())    
    if last_feed:
        if st.button("⏹ Stop Feed"):
            if last_feed:
                duration_str = update_feed(last_feed)
                st.success(f"Stopped feeding session! Duration: {duration_str}")
            else:
                st.warning("No ongoing feeding session found!")
            time.sleep(0.5)
            st.rerun()
       
    # Diaper Change Section
    st.header("🚽 Diaper Change")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚽 Pee Mum"):
            log_event("Pee", orientation="Mum")
            st.success("Logged pee diaper change!")
            time.sleep(0.5)
            st.rerun()
        if st.button("💩 Poo Mum"):
            log_event("Poop", orientation="Mum")
            st.success("Logged poo diaper change!")
            time.sleep(0.5)
            st.rerun()
        if st.button("🚽💩 Mixed Mum"):
            log_event("Mixed", orientation="Mum")
            st.success("Logged mixed diaper change!")
            time.sleep(0.5)
            st.rerun()
    with col2:
        if st.button("🚽 Pee Dad"):
            log_event("Pee", orientation="Dad")
            st.success("Logged pee diaper change!")
            time.sleep(0.5)
            st.rerun()
        if st.button("💩 Poo Dad"):
            log_event("Poop", orientation="Dad")
            st.success("Logged poo diaper change!")
            time.sleep(0.5)
            st.rerun()
        if st.button("🚽💩 Mixed Dad"):
            log_event("Mixed", orientation="Dad")
            st.success("Logged mixed diaper change!")
            time.sleep(0.5)
            st.rerun()

    # Display last diaper change with duration
    last_diaper_event, last_diaper_time = get_last_diaper_change()
    if last_diaper_time:
        last_diaper_time = format_as_datetime(last_diaper_time)
        duration = get_time() - last_diaper_time
        
    st.subheader("Today's Feed Counts")
    today_start, today_end, yesterday_start, yesterday_end = time_to_date()
    df_feeding_yesterday = get_data(event="Feeding", details="complete", 
                          start_date=yesterday_start, 
                          end_date=yesterday_end)
    df_feeding_today = get_data(event="Feeding", details="complete", 
                          start_date=today_start)
    try:
        if len(df_feeding_today)==1 and df_feeding_today.iloc[0, 0]==0:
            today_feeds=0
        else:
            today_feeds = len(df_feeding_today)
    except (TypeError, ValueError):
        today_feeds = 0
    yesterday_feeds = len(df_feeding_yesterday)

    col1, col2, col3 = st.columns(3)
    # Metric 1: Number of feeds
    with col1:
        st.metric(
            label="Number of Feeds Today", 
            value=today_feeds,
            delta=today_feeds - yesterday_feeds,
            delta_color="normal",
            border = True
        )
    # Metric 2: Total duration
    today_duration = int(df_feeding_today['duration_minutes'].sum())
    yesterday_duration = int(df_feeding_yesterday['duration_minutes'].sum())
    with col2:
        st.metric(
            label="Total Duration (min)", 
            value=round(today_duration, 1),
            delta=round(today_duration - yesterday_duration, 1),
            delta_color="normal",
            border = True
        )
    # Metric 3: Average duration per feed
    today_avg = df_feeding_today['duration_minutes'].mean()
    yesterday_avg = df_feeding_yesterday['duration_minutes'].mean()
    with col3:
        st.metric(
            label="Avg Duration per Feed (min)", 
            value=round(today_avg, 1) if not pd.isna(today_avg) else 0,
            delta=round(today_avg - yesterday_avg, 1) if not pd.isna(today_avg) else 0,
            delta_color="normal",
            border = True
        )
        
    st.subheader("Today's Diaper Counts")
    df_diaper_yesterday = get_data(event=['Pee','Poop','Mixed'], 
                                   start_date=yesterday_start,
                                   end_date=yesterday_end,
                                   countgroup=['event'])
    
    df_diaper_today = get_data(event = ['Pee', 'Poop', 'Mixed'],
                               start_date=today_start,
                               end_date=today_end,
                               countgroup=['event']
                               )
    df_diaper_yesterday = df_to_dict(df_diaper_yesterday)
    df_diaper_today = df_to_dict(df_diaper_today)
    total_diapers = (
        df_diaper_today.get('Pee', 0) + 
        df_diaper_today.get('Poop', 0) + 
        df_diaper_today.get('Mixed', 0)
    )
    yesterday_total_diapers = (
        df_diaper_yesterday.get('Pee', 0) + 
        df_diaper_yesterday.get('Poop', 0) + 
        df_diaper_yesterday.get('Mixed', 0)
        )
    time_since_pee = get_time_since_last('Pee')
    time_since_poop = get_time_since_last('Poop')
    time_since_mixed = get_time_since_last('Mixed')
    last_diaper_type, last_diaper_time_since = last_diaper(time_since_pee, time_since_poop, time_since_mixed)
    
    
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if df_diaper_today.get('Pee', 0) -  df_diaper_yesterday.get('Pee', 0) == 0:
            st.metric("Pee", df_diaper_today.get('Pee', 0), 0, border=True)
        else:
            st.metric("Pee", df_diaper_today.get('Pee', 0), df_diaper_today.get('Pee', 0) -  df_diaper_yesterday.get('Pee', 0), border=True)
        st.write(f"Last: {format_time_short(time_since_pee)}")
    with col2:
        if df_diaper_today.get('Poop', 0) -  df_diaper_yesterday.get('Poop', 0) == 0:
            st.metric("Poo", df_diaper_today.get('Poop', 0), 0, border=True)
        else:
            st.metric("Poo", df_diaper_today.get('Poop', 0), df_diaper_today.get('Poop', 0) -  df_diaper_yesterday.get('Poop', 0), border=True)
        st.write(f"Last: {format_time_short(time_since_poop)}")
    with col3:
        if df_diaper_today.get('Mixed', 0) -  df_diaper_yesterday.get('Mixed', 0) == 0:
            st.metric("Mixed", df_diaper_today.get('Mixed', 0), 0, border=True)
        else:
            st.metric("Mixed", df_diaper_today.get('Mixed', 0), df_diaper_today.get('Mixed', 0) -  df_diaper_yesterday.get('Mixed', 0), border=True)
        st.write(f"Last: {format_time_short(time_since_mixed)}")
    with col4:
        if total_diapers - yesterday_total_diapers == 0:
            st.metric("Total", total_diapers, 0, border=True)
        else:
            st.metric("Total", total_diapers, total_diapers - yesterday_total_diapers, border=True)
        st.write(
            f"Last {last_diaper_type}: {last_diaper_time_since}" if last_diaper_type else "No diapers")




with tab2:
    st.header("📊 Baby Metrics Visualizations")
    # Time period selection
    days_str = get_time() - get_min_date()
    days_to_show = st.slider("Number of days to show", 1, days_str.days, 7)
    
    # Diaper Changes Visualization
    st.subheader("Diaper Changes Over Time")
    diaper_data = get_data(event = ['Pee', 'Poop', 'Mixed'],
                            days=days_to_show,
                            countgroup=['event',"date(Timestamp)"]
                            )
    diaper_data = diaper_data.rename(columns={"date(Timestamp)": "Date", 
                                              "event": "Event", 
                                              "count": "Count",
                                              })
    df_totals = diaper_data.groupby('Date')['Count'].sum().reset_index()
    fig1 = px.bar(diaper_data, x='Date', y='Count', color='Event',
                    title=f"Diaper Changes by Type (Last {days_to_show} Days)",
                    labels={'Count': 'Number of Changes', 'Date': 'Date'},
                    barmode='group')
    fig1.add_scatter(x=df_totals['Date'], y=df_totals['Count'], 
                    mode='lines+markers',
                    name='Total',
                    line=dict(color='Green', width=2, dash='dot'),
                    marker=dict(symbol='diamond-open'))
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.line(diaper_data, x='Date', y='Count', color='Event',
                title=f"Diaper Change Trends (Last {days_to_show} Days)",
                markers=True)
    fig2.add_scatter(x=df_totals['Date'], y=df_totals['Count'], 
                    mode='lines+markers',
                    name='Total',
                    line=dict(color='Green', width=2, dash='dot'),
                    marker=dict(symbol='diamond-open'))
    st.plotly_chart(fig2, use_container_width=True)
    
    event_type = st.selectbox(
        "Select Diaper Event Type",
        options=["Total","Mixed", "Pee", "Poop"],
        index=0  # default to "mixed"
    )
    hourly_diaper_data = get_data(event = ['Pee', 'Poop', 'Mixed'],
                            days=days_to_show,
                            countgroup=['event',"Timestamp"]
                            )
    if event_type != "Total":
        hourly_diaper_data = hourly_diaper_data[hourly_diaper_data['event'] == event_type]
    ## assuming all time is the same timezone
    hourly_diaper_data_processed = timeseries_datetime(config, hourly_diaper_data)
    hourly_counts = hourly_diaper_data_processed.groupby(['Day', 'Hour']).size().reset_index(name='Count')
    hourly_counts['Cumulative'] = hourly_counts.groupby('Day')['Count'].cumsum()
    hourly_counts['Day'] = hourly_counts['Day'].astype(str)
    fig31 = px.line(hourly_counts, 
                x='Hour', 
                y='Cumulative', 
                color='Day',  # Each day gets its own line
                title=f"Cumulative {event_type.capitalize()} Diaper Changes by Hour (Last {days_to_show} Days)",
                markers=True,
                labels={
                    'Hour': 'Hour of Day', 
                    'Cumulative': 'Cumulative Count',
                    'Day': 'Date'
                })
    fig31.update_xaxes(tickvals=list(range(24)))
    fig31.update_layout(
        hovermode='x unified',
        legend_title_text='Date'
    )
    
    st.plotly_chart(fig31, use_container_width=True)

with tab3:
    st.subheader("Feeding Patterns")
    days_to_show2 = st.slider("Number of days to show ", 1, days_str.days, 7,)
    hourly_feeding_data = get_data(event = 'Feeding',
                        days=days_to_show2,
                        )
    df_feeding = timeseries_datetime(config, hourly_feeding_data, timestamp_column="timestamp")
    df_feeding['Day'] = pd.to_datetime(df_feeding['timestamp']).dt.day_name()
    df_feeding['Duration (min)'] = df_feeding['duration_minutes']
    df_feeding['Date'] = df_feeding['timestamp']
    # Average duration by day
    fig4 = px.bar(df_feeding.groupby('Day')['Duration (min)'].mean().reset_index(),
                    x='Day', y='Duration (min)',
                    title=f"Average Feeding Duration by Day (Last {days_to_show} Days)")
    st.plotly_chart(fig4, use_container_width=True)
    fig5_1 = px.bar(df_feeding.groupby('Day')['Duration (min)'].sum().reset_index(),
                    x='Day', y='Duration (min)',
                    title=f"Sum Feeding Duration by Day (Last {days_to_show} Days)")
    st.plotly_chart(fig5_1, use_container_width=True)
    fig5_2 = px.bar(df_feeding.groupby('Day')['Duration (min)'].count().reset_index(),
                    x='Day', y='Duration (min)',
                    labels={'Duration (min)': 'Count'},
                    title=f"Number of Feeds by Day (Last {days_to_show} Days)")
    st.plotly_chart(fig5_2, use_container_width=True)
    
    df_feeding['timestamp'] = pd.to_datetime(df_feeding['timestamp'])
    df_feeding['Date'] = df_feeding['timestamp'].dt.date
    df_feeding['Time2'] = df_feeding['timestamp'].apply(lambda x: x.replace(year=1900, month=1, day=1))
    
    fig5 = px.scatter(df_feeding, x='Date', y='Time2',
                    size='Duration (min)',
                    title=f"Feeding Times and Durations (Last {days_to_show} Days)",
                    labels={'Time': 'Time of Day'})
    fig5.update_layout(
        yaxis=dict(
            tickformat='%H',  # Format time as hours and minutes
            title="Time of Day"
        )
    )
    # Display the plot in Streamlit
    st.plotly_chart(fig5, use_container_width=True)

    df_feeding
    days_to_show_2 = st.slider("Select number of days to show", 1, 30, 1)
    if days_to_show_2 != days_to_show:
        day_filter = days_to_show_2
    else:
        day_filter = days_to_show
    df_feeding_2 = df_feeding.sort_values('timestamp').reset_index(drop=True)
    df_feeding_2 = df_feeding_2[df_feeding_2['Date'] >= df_feeding_2['Date'].max() - timedelta(days=day_filter-1)]
    df_feeding_2['time_since_last_feed'] = df_feeding_2['timestamp'].diff()
    df_feeding_2['hours_since_last_feed'] = df_feeding_2['time_since_last_feed'].dt.total_seconds() / 3600

    # Calculate average and standard deviation
    avg_hours = df_feeding_2['hours_since_last_feed'].mean()
    std_hours = df_feeding_2['hours_since_last_feed'].std()

    # Create scatter plot with hours
    fig5_1 = px.scatter(
        df_feeding_2,
        x='timestamp',
        y='hours_since_last_feed',
        title=f"Time Between Feeds (Last {day_filter} Days) - Avg: {avg_hours:.1f}±{std_hours:.1f} hours",
        labels={'hours_since_last_feed': 'Hours Since Last Feed', 'datetime': 'Feeding Time'},
        hover_data=['time_since_last_feed']
    )

    # Add average line
    fig5_1.add_hline(
        y=avg_hours,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Average: {avg_hours:.1f} hours",
        annotation_position="bottom right"
    )

    # Add standard deviation bands
    fig5_1.add_hrect(
        y0=avg_hours - std_hours,
        y1=avg_hours + std_hours,
        fillcolor="lightgreen",
        opacity=0.1,
        line_width=0,
        annotation_text=f"±1 std dev",
        annotation_position="bottom right"
    )

    # Optional: Add 2 standard deviation bands
    fig5_1.add_hrect(
        y0=avg_hours - 2*std_hours,
        y1=avg_hours + 2*std_hours,
        fillcolor="lightyellow",
        opacity=0.2,
        line_width=0,
        annotation_text=f"±2 std dev",
        annotation_position="bottom right"
    )

    # Customize hover format
    fig5_1.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Hours since last feed: %{y:.1f}<br>"
            "Raw difference: %{customdata[0]}"
        ),
        marker=dict(size=10, color='blue')  # Customize marker appearance
    )

    # Improve y-axis formatting
    fig5_1.update_yaxes(
        title_text="Hours Since Last Feed",
        tickformat=".1f",
        range=[0, max(df_feeding_2['hours_since_last_feed']) * 1.1]  # Add 10% padding
    )

    # Improve layout
    fig5_1.update_layout(
        showlegend=False,
        hovermode="x unified"
    )

    st.plotly_chart(fig5_1, use_container_width=True)

    st.markdown(f"""
    **Statistics for last {day_filter} days:**
    - Average time between feeds: **{avg_hours:.1f} hours**
    - Standard deviation: **{std_hours:.1f} hours**
    - Minimum: **{df_feeding_2['hours_since_last_feed'].min():.1f} hours**
    - Maximum: **{df_feeding_2['hours_since_last_feed'].max():.1f} hours**
    """)

    
    # Duration distribution
    fig6 = px.histogram(df_feeding, x='Duration (min)',
                        title=f"Feeding Duration Distribution (Last {days_to_show} Days)",
                        nbins=20)
    st.plotly_chart(fig6, use_container_width=True)

with tab4:
    # Weight Visualisation
    st.subheader("Weight")
    weight_data = get_all_weight_data(100000)
    if weight_data:
        weight_data = pd.DataFrame(weight_data, columns=['Date', 'Event', 'Weight'])
        fig7 = px.line(weight_data, x='Date', y='Weight', title=f"Weight", markers=True)
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.warning("No weight data available for the selected period")
        



with tab5:
    st.subheader("All Logs")
    
    # Load the logs from the database
    filtered_logs = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", conn)
    filtered_logs = timeseries_datetime(config, filtered_logs, timestamp_column="timestamp")
    # Display editable dataframe
    edited_logs = st.data_editor(
        filtered_logs,
        disabled=["id"],  # Prevent editing of ID and timestamp
        num_rows="dynamic",
        key="logs_editor"
    )
    
    # Compare edited logs with original to find changes
    if not edited_logs.equals(filtered_logs):
        # Get the differences
        changes = edited_logs.compare(filtered_logs)
        
        if not changes.empty:
            # Update the database with changes
            cursor = conn.cursor()
            
            try:
                for idx, row in edited_logs.iterrows():
                    original_row = filtered_logs.loc[idx]
                    
                    # Check if any editable field has changed
                    editable_columns = [col for col in edited_logs.columns if col not in ['id']]
                    changes_made = False
                    
                    update_values = {}
                    for col in editable_columns:
                        if row[col] != original_row[col]:
                            update_values[col] = row[col]
                            changes_made = True
                    
                    if changes_made:
                        if 'timestamp' in update_values:
                            update_values['timestamp'] = update_values['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    
                        # Build the update query
                        set_clause = ", ".join([f"{col} = ?" for col in update_values.keys()])
                        query = f"UPDATE logs SET {set_clause} WHERE id = ?"
                        
                        # Execute the update
                        cursor.execute(query, list(update_values.values()) + [row['id']])
                
                conn.commit()
                st.success("Changes saved to database!")
                
                # Refresh the data
                filtered_logs = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC", conn)
                st.rerun()
            except Exception as e:
                conn.rollback()
                st.error(f"Error updating database: {e}")
            finally:
                cursor.close()
    
    # Add new record form
    st.write("### Add New Record")
    with st.form("add_record_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_event = st.selectbox(
                "Event Type",
                ["Feeding", "Pee", "Poop", "Mixed", "Other"],
                key="new_event"
            )
            new_details = st.text_input("Details", key="new_details")
        
        with col2:
            new_comments = st.text_area("Comments", key="new_comments")
            new_orientation = st.selectbox(
                "Orientation (for feeding)",
                ["", "Left", "Right"],
                key="new_orientation"
            )
        
        submitted = st.form_submit_button("Add Record")
        if submitted:
            try:
                log_event(
                    event=new_event,
                    details=new_details,
                    comments=new_comments if new_comments else None,
                    orientation=new_orientation if new_orientation else None
                )
                st.success("Record added successfully!")
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Error adding record: {str(e)}")
    
    # Delete record section
    st.write("### Delete Record")
    record_to_delete = st.selectbox(
        "Select record to delete",
            filtered_logs['id'].astype(str) + " - " + 
            filtered_logs['event'] + " - " + 
            filtered_logs['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S'),
        index=0,
        key="delete_select"
    )
    
    if st.button("Delete Selected Record"):
        try:
            record_id = int(record_to_delete.split(" - ")[0])
            c = conn.cursor()
            c.execute("DELETE FROM logs WHERE id = ?", (record_id,))
            conn.commit()
            st.success("Record deleted successfully!")
            time.sleep(0.5)
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting record: {str(e)}")