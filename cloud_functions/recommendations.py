from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json
import functions_framework
from flask import request
from google.cloud import secretmanager
from datetime import datetime, timedelta
from google.cloud import storage


def get_secret(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    #name = f"projects/474541342246/secrets/{secret_id}"
    response = client.access_secret_version(name=name)
    secret_payload = response.payload.data.decode('UTF-8')
    return secret_payload

@functions_framework.http
def get_user_playlists(request):
    try:
        if request.method != 'POST':
            return 'Invalid request method. Only POST is allowed.', 405
        if not request.is_json:
            return 'Invalid request format. Expected JSON.', 400

        request_data = request.get_json()

        user_id = request_data.get('user_id')
        if user_id is None:
            return 'Missing user_id in request body.', 400
            
        project_id = os.environ.get('PROJECT_ID')
        top_tracks_bucket = os.environ['TRACK_RECOMMENDATIONS']
        secret_id = "BIGQUERY_KEY"
        
        if not project_id:
            return 'Environment variables not set', 500

        storage_client = storage.Client()
        bucket = storage_client.bucket(top_tracks_bucket)

        # Access the API token from Secret Manager
        api_token = get_secret(project_id, secret_id)
        credentials = service_account.Credentials.from_service_account_info(json.loads(api_token))
        client = bigquery.Client(credentials=credentials, project=project_id, location="europe-west4")

        table_id_playlists = f"{project_id}.project.Playlists"
        
        query = f"""
            SELECT * FROM {table_id_playlists} 
            WHERE user_id = "{user_id}"
        """
        query_job = client.query(query)
        results = query_job.result()
        playlists = []
        for row in results:
            playlists.append(row['playlist_id'])

        if not playlists:
            return f'No playlists found for user_id: {user_id}', 404

        today = datetime.utcnow() + timedelta(hours=1)
        last_sunday = today - timedelta(days=today.weekday() + 1)  # Get last Sunday
        start_date = (last_sunday).strftime('%Y-%m-%d')  # Last Sunday to Saturday
        end_date = (last_sunday + timedelta(days=6)).strftime('%Y-%m-%d')

        formatted_time = last_sunday.strftime("%Y-%m-%d %H:%M:%S") + " UTC"

        query = f"""SELECT Tracks.genre_id, Tracks.track_id
                FROM `{project_id}.project.PlaylistsTracks` AS PlaylistsTracks
                JOIN `{project_id}.project.Tracks` AS Tracks
                ON PlaylistsTracks.track_id = Tracks.track_id
                WHERE PlaylistsTracks.date_added > '{formatted_time}' AND PlaylistsTracks.playlist_id IN ("""
        for playlist in playlists:
            query += f" {playlist}, "
        
        query = query[:-2]
        query += f") ORDER BY PlaylistsTracks.date_added DESC LIMIT 20"
        print("query", query)
        query_job = client.query(query)
        results = query_job.result()

        tracks = []
        genres = []
        
        for row in results:
            print("row", row)
            tracks.append(row['track_id'])
            genres.append(row['genre_id'])
            print("track_id", row['track_id'])
            print("genre_id", row['genre_id'])
        
        filename = f'top-weekly-tracks-{start_date}-to-{end_date}.json'
        blob = bucket.blob(filename)
        recommendations=[]
        number_of_recommendations=6
        if blob.exists():
            log_content = blob.download_as_string()
            top_global_tracks = json.loads(log_content)
            for text in top_global_tracks:
                if(number_of_recommendations==0):
                    break
                text = text.strip()
                text_int = int(text)
                print(f"Checking if text '{text}' is in tracks {tracks}")
                if text_int in tracks:
                    print("REPETIDO")
                    continue
                query = f"""SELECT Tracks.genre_id
                        FROM `{project_id}.project.Tracks` AS Tracks
                        WHERE Tracks.track_id = {text} """
                print("query", query)
                query_job = client.query(query)
                results = query_job.result()
                for row in results:
                    print("row ", row['genre_id'])
                    print("row tr", text)
                    if(row['genre_id'] in genres):
                        recommendations.append(text)
                        number_of_recommendations-=1        
            print(number_of_recommendations)
        else:
            print("blob doesnt exist")

        if(number_of_recommendations>0):
            # Convert the lists to a comma-separated string
            tracks_str = ', '.join(map(str, tracks))
            genres_str = ', '.join(map(str, genres))
            recommendations_str = ', '.join(map(str, recommendations))
            query = f"""
                    SELECT Tracks.track_id
                    FROM `{project_id}.project.Tracks` AS Tracks
                    WHERE Tracks.track_id NOT IN ({tracks_str})
                    AND Tracks.genre_id IN ({genres_str})
                    AND Tracks.track_id NOT IN ({recommendations_str})
                    LIMIT {number_of_recommendations}"""
            print("query", query)
            query_job = client.query(query)
            results = query_job.result()
            for row in results:
                print("randomtracks",row['track_id'])
                recommendations.append(row['track_id'])

        
        rec_filename = f'recommendations-{user_id}-{start_date}-to-{end_date}.json'
        blob = bucket.blob(rec_filename)
        blob.upload_from_string(json.dumps({f'{user_id}_recommendations': recommendations}))
        return json.dumps({f'{user_id}_recommendations': recommendations}), 200
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return f'An error occurred: {str(e)}', 500
