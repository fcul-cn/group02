from datetime import datetime, timedelta
from google.cloud import logging
from google.cloud import storage
import json
import os
import functions_framework
from flask import Flask, request
import re


@functions_framework.http
def daily_logs(request):
    #print("Received request")
    try:
        if not request.is_json:
            #print("Request is not JSON")
            return 'Invalid request format', 400

        request_data = request.get_json()
        #print("Request JSON:", request_data)
        project_id = os.environ['PROJECT_ID']
        bucket_name = os.environ['WARM_BUCKET'] 
        #print("variable bucket", bucket_name)
        #print("variable id", project_id)
        if not project_id or not bucket_name:
            #print("Environment variables are not set")
            return 'Environment variables not set', 500

        logging_client = logging.Client(project=project_id)
        #print("clientt", logging_client)

        yesterday = datetime.utcnow() - timedelta(days=1, hours=-1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        #print("now", datetime.utcnow())
        #print("yesterday", yesterday_str)

        start_timestamp = datetime(yesterday.year, yesterday.month, yesterday.day)
        end_timestamp = start_timestamp + timedelta(days=1) - timedelta(microseconds=1)
        #filter_ = f'severity>=ERROR AND timestamp>="{start_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")}" AND timestamp<="{end_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")}"'
        filter_ = f'severity>=ERROR AND NOT textPayload:"cert" AND NOT textPayload:"/health" AND NOT textPayload:"Running" AND NOT textPayload:"WARNING" AND NOT textPayload:"CTRL+C" AND NOT "/healthcheck" AND timestamp>="{start_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")}" AND timestamp<="{end_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")}"'
        logs = logging_client.list_entries(
            filter_=filter_,
            order_by=logging.DESCENDING,
            page_size=2500
        )
        #print("logs", logs)
        log_data = {}

        #ISO 8601 timestamps ex: 2024-06-14T17:56:14.584Z
        iso_timestamp_regex = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z')
        #ex: [14/Jun/2024 17:34:10]
        bracket_timestamp_regex = re.compile(r'\[\d{2}/[A-Za-z]{3}/\d{4} \d{2}:\d{2}:\d{2}\]')
        #ex: [2024-06-15 14:15:20,891]
        detailed_bracket_timestamp_regex = re.compile(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}\]')

        #GET /api/auth/callback? has different codes. removal of this code might be helpful to aggregate the callback logs

        for entry in logs:
            #error_message = entry.payload
            error_message = json.dumps(entry.payload)
            #print("payload", error_message)
            error_message = re.sub(iso_timestamp_regex, '', error_message)
            error_message = re.sub(bracket_timestamp_regex, '', error_message)
            error_message = re.sub(detailed_bracket_timestamp_regex, '', error_message)
            if error_message not in log_data:
                log_data[error_message] = {
                    'count': 0,
                    'first_timestamp': None,
                    'last_timestamp': None
                }
            log_data[error_message]['count'] += 1
            if log_data[error_message]['first_timestamp'] is None or entry.timestamp < log_data[error_message]['first_timestamp']:
                log_data[error_message]['first_timestamp'] = entry.timestamp
            if log_data[error_message]['last_timestamp'] is None or entry.timestamp > log_data[error_message]['last_timestamp']:
                log_data[error_message]['last_timestamp'] = entry.timestamp

        data = {
            'date': yesterday_str,
            'errors': [
                {
                    'message': error_message,
                    'count': log_data[error_message]['count'],
                    'first_timestamp': log_data[error_message]['first_timestamp'].isoformat() if log_data[error_message]['first_timestamp'] else None,
                    'last_timestamp': log_data[error_message]['last_timestamp'].isoformat() if log_data[error_message]['last_timestamp'] else None
                } for error_message in log_data
            ]
        }

        #formatted_data = json.dumps(data, indent=4)

        filename = f'logs-{yesterday_str}.json'
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(json.dumps(data))
        
        return 'Logs aggregated and uploaded successfully.', 200
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return f'An error occurred: {str(e)}', 500