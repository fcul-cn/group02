import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from playlist_pb2 import (
    Playlist,
    GetPlaylistResponse,
    DeletePlaylistResponse,
    AddPlaylistResponse,
    GetPlaylistTracksResponse,
    AddTrackToPlaylistResponse,
    DeleteTrackFromPlaylistResponse
)
import playlist_pb2_grpc
from datetime import datetime
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

class PlaylistService(playlist_pb2_grpc.PlaylistServiceServicer):
    def getPLaylist(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return GetPlaylistResponse(playlist=Playlist(
                        playlist_id=row[0],
                        user_id=row[1],
                        playlist_name=row[2],
                        date_created=str(row[3]),
                    )
                )
            raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
         
    def deletePlaylist(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            row = cur.fetchone()
            if not (row is None):
                response = DeletePlaylistResponse(playlist=Playlist(
                        playlist_id=row[0],
                        user_id=row[1],
                        playlist_name=row[2],
                        date_created=str(row[3]),
                    )
                )
                query = sql.SQL("DELETE FROM Playlist WHERE playlist_id = %s;") 
                cur.execute(query, (request.playlist_id,))
                conn.commit()
                return response
            raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def addPlaylist(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL(
                "INSERT INTO Playlist (user_id, playlist_name) VALUES (%s,%s) RETURNING playlist_id;") 
            cur.execute(query, (request.playlist.user_id, request.playlist.playlist_name))
            playlist_id = cur.fetchone()[0]
            print(playlist_id)
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (playlist_id,))
            row = cur.fetchone()
            print(row)
            conn.commit()
            if not (row is None):
                return AddPlaylistResponse(playlist=Playlist(
                        playlist_id=row[0],
                        user_id=row[1],
                        playlist_name=row[2],
                        date_created=str(row[3]),
                    )
                )
            raise InvalidArgument()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def getPLaylistTracks(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT track_id FROM PlaylistTracks WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            rows = cur.fetchall()
            conn.commit()
            if not (rows is None):
                tracks=[]#######provavelmente fazer isto no logic
                for row in rows:
                    track_id=row[0]
                    url = 'http://track-service/api/tracks/{}'.format(track_id)
                    response = requests.get(url)
                    if response.status_code == 200:
                        track_details = response.json()
                        tracks.append(track_details)
                return GetPlaylistTracksResponse(tracks=tracks)#############
            raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def deleteTrackFromPlaylist(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (request.playlist_id,))
            row = cur.fetchone()
            if not (row is None):
                response = DeleteTrackFromPlaylistResponse(playlist=Playlist(
                        playlist_id=row[0],
                        user_id=row[1],
                        playlist_name=row[2],
                        date_created=str(row[3]),
                    )
                )
                query = sql.SQL("DELETE FROM PlaylistTrack WHERE playlist_id = %s AND track_id = %s;") 
                cur.execute(query, (request.playlist_id, request.track_id,))
                conn.commit()
                return response
            raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def addTrackToPlaylist(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL(
                "INSERT INTO PlaylistTrack (playlist_id, track_id) VALUES (%s,%s) RETURNING playlist_id;") 
            cur.execute(query, (request.playlist_id, request.track_id))
            playlist_id = cur.fetchone()[0]
            print(playlist_id)
            query = sql.SQL("SELECT * FROM Playlist WHERE playlist_id = %s;") 
            cur.execute(query, (playlist_id,))
            row = cur.fetchone()
            print(row)
            conn.commit()
            if not (row is None):
                return AddTrackToPlaylistResponse(playlist=Playlist(
                        playlist_id=row[0],
                        user_id=row[1],
                        playlist_name=row[2],
                        date_created=str(row[3]),
                    )
                )
            raise InvalidArgument()
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
    playlist_pb2_grpc.add_PlaylistServiceServicer_to_server(
        PlaylistService(), server
    )
    server.add_insecure_port("[::]:50057")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
