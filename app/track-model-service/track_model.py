import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import Track, GetTrackResponse, DeleteTrackResponse, AddTrackResponse, GetTrackGenreResponse, GetGenreTracksResponse
import app_pb2_grpc
from grpc_interceptor.exceptions import NotFound, InvalidArgument, AlreadyExists
from grpc_health.v1.health import HealthServicer
from grpc_health.v1 import health_pb2, health_pb2_grpc

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

class TrackService(app_pb2_grpc.TrackServiceServicer):
    def getTrack(self, request, context):
        try:
            if request.track_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Track's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Tracks WHERE track_id = %s;") 
            cur.execute(query, (request.track_id,))
            row = cur.fetchone()
            conn.commit()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Track not found.")
                context.abort()
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
                ))
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
         
    def deleteTrack(self, request, context):
        try:
            if request.track_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Track's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Tracks WHERE track_id = %s;") 
            cur.execute(query, (request.track_id,))
            row = cur.fetchone()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Track not found.")
                context.abort()
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
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def addTrack(self, request, context):
        if request.track.genre_id <= 0 or request.track.subgenre_id <= 0 or request.track.release_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Genres's and Release's ids must be higher than 0.")
                context.abort()
        check_if_title_exists = sql.SQL("SELECT 1 FROM Tracks WHERE title = %s")
        check_if_mix_exists = sql.SQL("SELECT 1 FROM Tracks WHERE mix = %s")
        check_if_track_url_exists = sql.SQL("SELECT 1 FROM Tracks WHERE track_url = %s")
        query = sql.SQL("INSERT INTO Tracks (title, mix, is_remixed, release_id, release_date, genre_id, subgenre_id, track_url, bpm, duration) VALUES (%s,%s,%s,%s,TO_DATE(%s, 'YYYY/MM/DD'),%s,%s,%s,%s,%s) RETURNING track_id;") 
        try:
            if not request.track.title or not request.track.mix or not request.track.release_date or not request.track.track_url:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Bad request body.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            cur.execute(check_if_title_exists, (request.track.title,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Track´s title already exists.")
                context.abort()
            cur.execute(check_if_mix_exists, (request.track.mix,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Track´s mix already exists.")
                context.abort()
            cur.execute(check_if_track_url_exists, (request.track.track_url,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Track´s URL already exists.")
                context.abort()
            cur.execute(query, (request.track.title, request.track.mix, request.track.is_remixed, request.track.release_id, request.track.release_date, request.track.genre_id, request.track.subgenre_id, request.track.track_url, request.track.bpm, request.track.duration))
            track_id = cur.fetchone()[0]
            query = sql.SQL("SELECT * FROM Tracks WHERE track_id = %s;") 
            cur.execute(query, (track_id,))
            row = cur.fetchone()
            conn.commit()
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
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def getTrackGenre(self, request, context):
        try:
            if request.track_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Track's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT genre_id FROM Tracks WHERE track_id = %s;") 
            cur.execute(query, (request.track_id,))
            row = cur.fetchone()
            conn.commit()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Track not found.")
                context.abort()
            return GetTrackGenreResponse(genre_id=row[0])
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def getGenreTracks(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Tracks WHERE genre_id = %s;") 
            cur.execute(query, (request.genre_id,))
            rows = cur.fetchall()
            conn.commit()
            tracks = []
            for row in rows:
                tracks.append(Track(
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
                ))
            return GetGenreTracksResponse(track=tracks)
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

class HealthServicer(health_pb2_grpc.HealthServicer):
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)
        
        
def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    app_pb2_grpc.add_TrackServiceServicer_to_server(
        TrackService(), server
    )
    
     # Add HealthServicer to the server.
    health_pb2_grpc.add_HealthServicer_to_server(
        HealthServicer(), server
    )
    
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
