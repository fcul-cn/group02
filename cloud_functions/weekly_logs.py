from datetime import datetime, timedelta
from google.cloud import storage
import json
import os
import functions_framework
import re

@functions_framework.http
def weekly_logs(request):
    print("Received request")
    try:
        if request.method != 'POST':
            return 'Invalid request method. Only POST is allowed.', 405
        if not request.is_json:
            return 'Invalid request format. Expected JSON.', 400

        request_data = request.get_json()

        number_of_top_tracks = request_data.get('number_of_top_tracks')
        if number_of_top_tracks is None:
            number_of_top_tracks = 20

        # Access bucket name from environment variables
        bucket_name = os.environ['WARM_BUCKET'] 
        bucket_name2 = os.environ['COLD_BUCKET']
        bucket_name3 = os.environ['TRACK_RECOMMENDATIONS']
        if not bucket_name or not bucket_name2:
            print("Environment variables are not set")
            return 'Environment variables not set', 500

        # Initialize Cloud Storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        today = datetime.utcnow() + timedelta(hours=1)
        # Determine the date range for the past week (Sunday to Saturday)
        last_sunday = today - timedelta(days=today.weekday() + 1)  # Get last Sunday
        start_date = (last_sunday).strftime('%Y-%m-%d')  # Last Sunday to Saturday
        end_date = (last_sunday + timedelta(days=6)).strftime('%Y-%m-%d')
        print("today", today)
        print("lastsunday", last_sunday)
        print("Date range:", start_date, "to", end_date)

        # Initialize aggregated log data
        aggregated_data = {}
        
        # Iterate over each day of the past week and retrieve logs
        for i in range(7):
            day = last_sunday + timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            filename = f'logs-{day_str}.json'
            blob = bucket.blob(filename)
            if blob.exists():
                log_content = blob.download_as_string()
                day_logs = json.loads(log_content)
                for error in day_logs['errors']:
                    message = error['message']
                    if message not in aggregated_data:
                        aggregated_data[message] = {
                            'count': 0,
                            'first_timestamp': None,
                            'last_timestamp': None
                        }
                    aggregated_data[message]['count'] += error['count']
                    first_ts = error['first_timestamp']
                    last_ts = error['last_timestamp']
                    if aggregated_data[message]['first_timestamp'] is None or (first_ts and first_ts < aggregated_data[message]['first_timestamp']):
                        aggregated_data[message]['first_timestamp'] = first_ts
                    if aggregated_data[message]['last_timestamp'] is None or (last_ts and last_ts > aggregated_data[message]['last_timestamp']):
                        aggregated_data[message]['last_timestamp'] = last_ts

        # Prepare final aggregated data
        weekly_data = {
            'week_start': start_date,
            'week_end': end_date,
            'errors': [
                {
                    'message': message,
                    'count': aggregated_data[message]['count'],
                    'first_timestamp': aggregated_data[message]['first_timestamp'],
                    'last_timestamp': aggregated_data[message]['last_timestamp']
                } for message in aggregated_data
            ]
        }

        filtered_messages = {message: data for message, data in aggregated_data.items() if "GET /api/tracks/" in message}

        # Sort the filtered messages by count in descending order and select the top 20
        sorted_messages = sorted(filtered_messages.items(), key=lambda x: x[1]['count'], reverse=True)[:number_of_top_tracks]

        track_data = {}
        top_track_ids = [] 
        for message, data in sorted_messages:
            match = re.search(r"GET /api/tracks/(\d+)", message)
            if match:
                track_id = match.group(1)
                track_data[track_id] = data
                top_track_ids.append(track_id)

        # Print each of the top 20 track_ids
        for track_id in top_track_ids:
            print("track_id",track_id)

        storage_client2 = storage.Client()
        bucket2 = storage_client2.bucket(bucket_name2)
        # Write aggregated data to Cloud Storage
        weekly_filename = f'weekly-logs-{start_date}-to-{end_date}.json'
        blob = bucket2.blob(weekly_filename)
        blob.upload_from_string(json.dumps(weekly_data))

        storage_client2 = storage.Client()
        bucket2 = storage_client2.bucket(bucket_name3)
        # Write aggregated data to Cloud Storage
        weekly_filename = f'top-weekly-tracks-{start_date}-to-{end_date}.json'
        blob = bucket2.blob(weekly_filename)
        blob.upload_from_string(json.dumps(top_track_ids))
        
        return 'Weekly logs aggregated and uploaded successfully.', 200
    except Exception as e:
        # Log the exception
        print(f'An error occurred: {str(e)}')
        return f'An error occurred: {str(e)}', 500