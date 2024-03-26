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
                return GetTrackResponse(
                    Track(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                        row[8],
                        row[9],
                        row[10],
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
                response = DeleteTrackResponse(
                    Track(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                        row[8],
                        row[9],
                        row[10],
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
                "INSERT INTO Tracks (title, mix, is_remixed, release_id, release_date, genre_id, subgenre_id, track_url, bpm, duration) VALUES (%s,%s,%s,TO_DATE(%s, 'YYYY/MM/DD'),%s,%s,%s,%s,%s) RETURNING track_id;") 
            cur.execute(query, (request.track,))
            track_id = cur.fetchone()[0]
            query = sql.SQL("SELECT * FROM Tracks WHERE track_id = %s;") 
            cur.execute(query, (track_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return AddTrackResponse(
                    Track(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                        row[8],
                        row[9],
                        row[10],
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
        return GetTrackGenreResponse()


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
