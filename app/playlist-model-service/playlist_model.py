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
from grpc_interceptor.exceptions import NotFound, InvalidArgument

def connect():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'),
            port=os.environ.get('POSTGRES_PORT'),
            database=os.environ.get('POSTGRES_DB')
        )
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

class PlaylistService(app_pb2_grpc.PlaylistServiceServicer):
    def getPlaylist(self, request, context):
        try:
            if request.playlist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Playlist's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            row = cur.fetchone()
            conn.commit()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Playlist not found.")
                context.abort()
            return GetPlaylistResponse(playlist=Playlist(
                    playlist_id=row[0],
                    user_id=row[1],
                    playlist_name=row[2],
                    date_created=str(row[3]),
                )
            )   
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
         
    def deletePlaylist(self, request, context):
        try:
            if request.playlist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Playlist's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            row = cur.fetchone()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Playlist not found.")
                context.abort()
            query = sql.SQL("DELETE FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            conn.commit()
            return DeletePlaylistResponse(playlist=Playlist(
                    playlist_id=row[0],
                    user_id=row[1],
                    playlist_name=row[2],
                    date_created=str(row[3]),
                )
            )   
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def addPlaylist(self, request, context):
        try:
            if request.playlist.user_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("User's id must be higher than 0.")
                context.abort()
            if not request.playlist.playlist_name:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Bad request body.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL(
                "INSERT INTO Playlist (user_id, playlist_name) VALUES (%s,%s) RETURNING playlist_id;") 
            cur.execute(query, (request.playlist.user_id, request.playlist.playlist_name))
            playlist_id = cur.fetchone()[0]
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (playlist_id,))
            row = cur.fetchone()
            conn.commit()
            return AddPlaylistResponse(playlist=Playlist(
                    playlist_id=row[0],
                    user_id=row[1],
                    playlist_name=row[2],
                    date_created=str(row[3]),
                )
            )
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def getPlaylistTracks(self, request, context):
        try:
            if request.playlist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Playlist's and track's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            row = cur.fetchone()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Playlist not found.")
                context.abort()
            query = sql.SQL("SELECT track_id FROM PlaylistTrack WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            rows = cur.fetchall()
            conn.commit()
            tracks = []
            for row in rows:
                tracks.append(row[0])  
            return GetPlaylistTracksResponse(track_ids=tracks)
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def updatePlaylistTracks(self, request, context):
        try:
            if request.playlist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Playlist's must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            row = cur.fetchone()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Playlist not found.")
                context.abort()
            query = sql.SQL("SELECT 1 FROM PlaylistTrack WHERE playlist_id = %s AND track_id = %s;")
            update_query = sql.SQL("INSERT INTO PlaylistTrack (playlist_id, track_id) VALUES (%s,%s);") 
            for track_id in request.add_tracks_ids:
                cur.execute(query, (request.playlist_id, track_id))
                if not cur.fetchone():
                    cur.execute(update_query, (request.playlist_id, track_id))
            query = sql.SQL("DELETE FROM PlaylistTrack WHERE playlist_id = %s AND track_id = %s;")  
            for track_id in request.delete_tracks_ids:
                cur.execute(query, (request.playlist_id, track_id))
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            row = cur.fetchone()
            conn.commit()
            return UpdatePlaylistResponse(playlist=Playlist(
                    playlist_id=row[0],
                    user_id=row[1],
                    playlist_name=row[2],
                    date_created=str(row[3]),
                )
            )
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def deleteTrackFromPlaylists(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("DELETE FROM PlaylistTrack WHERE track_id = %s;") 
            cur.execute(query, (request.track_id,))
            conn.commit()
            return DeleteTrackFromPlaylistsResponse()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    app_pb2_grpc.add_PlaylistServiceServicer_to_server(
        PlaylistService(), server
    )
    server.add_insecure_port("[::]:50057")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
