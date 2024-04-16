import psycopg2
from psycopg2 import sql
from concurrent import futures
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
json_file = json.loads(json_string)
credentials = service_account.Credentials.from_service_account_info(json_file)
client = bigquery.Client(credentials=credentials, location="europe-west4")
table_id_playlists = "confident-facet-329316.project.Playlists"
table_id_playlists_tracks = "confident-facet-329316.project.PlaylistsTracks"


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
        query = f"DELETE FROM {table_id_playlists} WHERE playlist_id = {request.playlist_id};" 
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
        if request.playlist.user_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("User's id must be higher than 0.")
            context.abort()
        if not request.playlist.playlist_name:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Bad request body.")
            context.abort()
        getMaxId = f"SELECT MAX(playlist_id) FROM {table_id_playlists};"
        query_job = client.query(getMaxId)
        result = query_job.result()
        playlist_id = list(result)[0][0] + 1
        row_to_insert = [
            {u"playlist_id": playlist_id, u"user_id": request.playlist.user_id, u"playlist_name": request.playlist.playlist_name}
        ]
        client.insert_rows_json(table_id_playlists, row_to_insert)
        get_new_playlist = f"SELECT * FROM {table_id_playlists} WHERE playlist_id = {playlist_id};"
        query_job = client.query(get_new_playlist)
        result = query_job.result()
        row = list(result)[0]
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
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist not found.")
            context.abort()
        query = f"SELECT track_id FROM {table_id_playlists_tracks} WHERE playlist_id = {request.playlist_id};" 
        query_job = client.query(query)
        result = query_job.result()
        rows = list(result)
        tracks = []
        for row in rows:
            tracks.append(row[0])  
        return GetPlaylistTracksResponse(track_ids=tracks)

    def updatePlaylistTracks(self, request, context):
        TODO()
        # if request.playlist_id <= 0:
        #     context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        #     context.set_details("Playlist's must be higher than 0.")
        #     context.abort()
        # conn = connect()
        # cur = conn.cursor()
        # query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
        # cur.execute(query, (request.playlist_id,))
        # row = cur.fetchone()
        # if (row is None):
        #     context.set_code(grpc.StatusCode.NOT_FOUND)
        #     context.set_details("Playlist not found.")
        #     context.abort()
        # query = sql.SQL("SELECT 1 FROM PlaylistTrack WHERE playlist_id = %s AND track_id = %s;")
        # update_query = sql.SQL("INSERT INTO PlaylistTrack (playlist_id, track_id) VALUES (%s,%s);") 
        # for track_id in request.add_tracks_ids:
        #     cur.execute(query, (request.playlist_id, track_id))
        #     if not cur.fetchone():
        #         cur.execute(update_query, (request.playlist_id, track_id))
        # query = sql.SQL("DELETE FROM PlaylistTrack WHERE playlist_id = %s AND track_id = %s;")  
        # for track_id in request.delete_tracks_ids:
        #     cur.execute(query, (request.playlist_id, track_id))
        # query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
        # cur.execute(query, (request.playlist_id,))
        # row = cur.fetchone()
        # conn.commit()
        # return UpdatePlaylistResponse(playlist=Playlist(
        #         playlist_id=row[0],
        #         user_id=row[1],
        #         playlist_name=row[2],
        #         date_created=str(row[3]),
        #     )
        # )

    def deleteTrackFromPlaylists(self, request, context):
        query = f"DELETE FROM {table_id_playlists_tracks} WHERE track_id = {request.track_id};" 
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
