from concurrent import futures
from datetime import datetime
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import (
    Playlist,
    GetPlaylistResponse,
    DeletePlaylistResponse,
    AddPlaylistResponse,
    GetPlaylistTracksResponse,
    UpdatePlaylistResponse,
    DeleteTrackFromPlaylistsResponse
)
import app_pb2_grpc
from grpc_interceptor.exceptions import NotFound, InvalidArgument, AlreadyExists
from grpc_health.v1.health import HealthServicer
from grpc_health.v1 import health_pb2, health_pb2_grpc
from google.cloud import bigquery
from google.oauth2 import service_account
import json, os

json_string = os.environ.get('API_TOKEN')
project_id = os.environ.get('PROJECT_ID')
json_file = json.loads(json_string)
credentials = service_account.Credentials.from_service_account_info(json_file)
client = bigquery.Client(credentials=credentials, location="europe-west4")
table_id_playlists = f"{project_id}.Playlists"
table_id_playlists_tracks = f"{project_id}.PlaylistsTracks"


class PlaylistService(app_pb2_grpc.PlaylistServiceServicer):
    def getPlaylist(self, request, context):
        if request.playlist_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Playlist's id must be higher than 0.")
            context.abort()
        query = f"SELECT * FROM {table_id_playlists} WHERE playlist_id = {request.playlist_id};" 
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist not found.")
            context.abort()
        row = list(result)[0]
        return GetPlaylistResponse(playlist=Playlist(
                playlist_id=row[0],
                user_id=row[1],
                playlist_name=row[2],
                date_created=str(row[3]),
            )
        )   
         
    def deletePlaylist(self, request, context):
        if request.playlist_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Playlist's id must be higher than 0.")
            context.abort()
        query = f"SELECT * FROM {table_id_playlists} WHERE playlist_id = {request.playlist_id};" 
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist not found.")
            context.abort()
        row = list(result)[0]
        print(row)
        query = f"DELETE {table_id_playlists} WHERE playlist_id = {request.playlist_id};" 
        query_job = client.query(query)
        query_job.result()
        return DeletePlaylistResponse(playlist=Playlist(
                playlist_id=row[0],
                user_id=row[1],
                playlist_name=row[2],
                date_created=str(row[3]),
            )
        )   

    def addPlaylist(self, request, context):
        if not request.playlist.user_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("User's id cannot be empty")
            context.abort()
        if not request.playlist.playlist_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Bad request body.")
            context.abort()
        getMaxId = f"SELECT MAX(playlist_id) FROM {table_id_playlists};"
        query_job = client.query(getMaxId)
        result = query_job.result()
        playlist_id = list(result)[0][0] + 1
        print(f"playlist_id: {playlist_id}")
        row_to_insert = [
            {u"playlist_id": playlist_id, u"user_id": request.playlist.user_id, u"playlist_name": request.playlist.playlist_name, u"date_created": datetime.now().strftime('%Y-%m-%d')}
        ]
        client.insert_rows_json(table_id_playlists, row_to_insert)
        get_new_playlist = f"SELECT * FROM {table_id_playlists} WHERE playlist_id = {playlist_id};"
        query_job = client.query(get_new_playlist)
        result = query_job.result()
        row = list(result)[0]
        print(row)
        return AddPlaylistResponse(playlist=Playlist(
                playlist_id=row[0],
                user_id=row[1],
                playlist_name=row[2],
                date_created=str(row[3]),
            )
        )

    def getPlaylistTracks(self, request, context):
        if request.playlist_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Playlist's and track's id must be higher than 0.")
            context.abort()
        query = f"SELECT * FROM {table_id_playlists} WHERE playlist_id = {request.playlist_id};"
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist not found.")
            context.abort()
        query = f"SELECT track_id FROM {table_id_playlists_tracks} WHERE playlist_id = {request.playlist_id};" 
        query_job = client.query(query)
        result = query_job.result()
        rows = list(result)
        print(rows)
        tracks = []
        for row in rows:
            tracks.append(row[0])  
        return GetPlaylistTracksResponse(track_ids=tracks)

    def updatePlaylistTracks(self, request, context):
        if request.playlist_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Playlist's must be higher than 0.")
            context.abort()
        query = f"SELECT * FROM {table_id_playlists} WHERE playlist_id = {request.playlist_id};" 
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist not found.")
            context.abort()
        for track_id in request.add_tracks_ids:
            query = f"SELECT 1 FROM {table_id_playlists_tracks} WHERE playlist_id = {request.playlist_id} AND track_id = {track_id};"
            query_job = client.query(query)
            result = query_job.result()
            if result.total_rows == 0:
                row_to_insert = [{u"playlist_id": request.playlist_id, u"track_id": track_id, u"date_added": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
                client.insert_rows_json(table_id_playlists_tracks, row_to_insert)
        for track_id in request.delete_tracks_ids:
            query = f"DELETE {table_id_playlists_tracks} WHERE playlist_id = {request.playlist_id} AND track_id = {track_id};" 
            query_job = client.query(query)
            query_job.result() 
        query = f"SELECT * FROM {table_id_playlists} WHERE playlist_id = {request.playlist_id};"
        query_job = client.query(query)
        result = query_job.result()
        row = list(result)[0]
        return UpdatePlaylistResponse(playlist=Playlist(
                playlist_id=row[0],
                user_id=row[1],
                playlist_name=row[2],
                date_created=str(row[3]),
            )
        )

    def deleteTrackFromPlaylists(self, request, context):
        query = f"DELETE {table_id_playlists_tracks} WHERE track_id = {request.track_id};" 
        query_job = client.query(query)
        result = query_job.result()
        return DeleteTrackFromPlaylistsResponse()

class HealthServicer(health_pb2_grpc.HealthServicer):
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)
        
def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    app_pb2_grpc.add_PlaylistServiceServicer_to_server(
        PlaylistService(), server
    )
    
    # Add HealthServicer to the server.
    health_pb2_grpc.add_HealthServicer_to_server(
        HealthServicer(), server
    )
    
    server.add_insecure_port("[::]:50057")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
