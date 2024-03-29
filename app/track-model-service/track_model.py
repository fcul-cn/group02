import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from track_pb2 import (
    Track,
    GetTrackResponse,
    DeleteTrackResponse,
    AddTrackResponse,
    GetTrackGenreResponse
)
import track_pb2_grpc
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

class TrackService(track_pb2_grpc.TrackServiceServicer):
    def getTrack(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Tracks WHERE track_id = %s;") 
            cur.execute(query, (request.track_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return GetTrackResponse(track=Track(
                        track_id=row[0],
                        title=row[1],
                        mix=row[2],
                        is_remixed=row[3],
                        release_id=row[4],
                        release_date=str(row[5]),
                        genre_id=row[6],
                        subgenre_id=row[7],
                        track_url=row[8],
                        bpm=row[9],
                        duration=row[10],
                    )
                )
            raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
         
    def deleteTrack(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Tracks WHERE track_id = %s;") 
            cur.execute(query, (request.track_id,))
            row = cur.fetchone()
            if not (row is None):
                response = DeleteTrackResponse(track=Track(
                        track_id=row[0],
                        title=row[1],
                        mix=row[2],
                        is_remixed=row[3],
                        release_id=row[4],
                        release_date=str(row[5]),
                        genre_id=row[6],
                        subgenre_id=row[7],
                        track_url=row[8],
                        bpm=row[9],
                        duration=row[10],
                    )
                )
                query = sql.SQL("DELETE FROM Tracks WHERE track_id = %s;") 
                cur.execute(query, (request.track_id,))
                conn.commit()
                return response
            raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def addTrack(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL(
                "INSERT INTO Tracks (title, mix, is_remixed, release_id, release_date, genre_id, subgenre_id, track_url, bpm, duration) VALUES (%s,%s,%s,%s,TO_DATE(%s, 'YYYY/MM/DD'),%s,%s,%s,%s,%s) RETURNING track_id;") 
            cur.execute(query, (request.track.title, request.track.mix, request.track.is_remixed, request.track.release_id, request.track.release_date, request.track.genre_id, request.track.subgenre_id, request.track.track_url, request.track.bpm, request.track.duration))
            track_id = cur.fetchone()[0]
            print(track_id)
            query = sql.SQL("SELECT * FROM Tracks WHERE track_id = %s;") 
            cur.execute(query, (track_id,))
            row = cur.fetchone()
            print(row)
            conn.commit()
            if not (row is None):
                return AddTrackResponse(track=Track(
                        track_id=row[0],
                        title=row[1],
                        mix=row[2],
                        is_remixed=row[3],
                        release_id=row[4],
                        release_date=str(row[5]),
                        genre_id=row[6],
                        subgenre_id=row[7],
                        track_url=row[8],
                        bpm=row[9],
                        duration=row[10],
                    )
                )
            raise InvalidArgument()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def getTrackGenre(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT genre_id FROM Tracks WHERE track_id = %s;") 
            cur.execute(query, (request.track_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return GetTrackResponse(genre_id=row[0])
            raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    track_pb2_grpc.add_TrackServiceServicer_to_server(
        TrackService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
