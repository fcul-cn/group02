import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import (
    Artist,
    GetArtistResponse,
    AddArtistResponse,
)
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

class ArtistService(app_pb2_grpc.ArtistService):
    def getArtist(self, request, context):
        try:
            artist_id = request.artist_id
            if artist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Artist's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Artist WHERE artist_id = %s")
            cur.execute(query, (artist_id,))
            row = cur.fetchone()
            conn.commit()
            if row is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Artist not found.")
                context.abort()
            if not (row is None):
                return GetArtistResponse(artist=Artist(
                        artist_id=row[0],
                        artist_name=row[1],
                        artist_url=row[2],
                        artist_updated_at=str(row[3]),
                    )
                )
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def addArtist(self, request, context):
        check_if_name_exists = sql.SQL("SELECT 1 FROM Artist WHERE artist_name = %s")
        check_if_url_exists = sql.SQL("SELECT 1 FROM Artist WHERE artist_url = %s")
        query = sql.SQL("INSERT INTO Artist (artist_name, artist_url, artist_updated_at) VALUES (%s, %s, %s) RETURNING artist_id;")
        get_new_artist = sql.SQL("SELECT * FROM Artist WHERE artist_id = %s;") 
        try:
            artist_name = request.artist.artist_name 
            artist_url = request.artist.artist_url
            if not artist_name or not artist_url:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Artist name and url are required.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            # Check if artist name or url already exists
            cur.execute(check_if_name_exists, (artist_name,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Artist name already exists.")
                context.abort()
            cur.execute(check_if_url_exists, (artist_url,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Artist URL already exists.")
                context.abort()
            # Add artist
            cur.execute(query, (artist_name, artist_url, request.artist.artist_updated_at))
            artist_id = cur.fetchone()[0]
            cur.execute(get_new_artist, (artist_id,))
            row = cur.fetchone()
            conn.commit()
            return AddArtistResponse(artist=Artist(
                    artist_id=row[0],
                    artist_name=row[1],
                    artist_url=row[2],
                    artist_updated_at=str(row[3]),
                )
            )
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
    app_pb2_grpc.add_ArtistServiceServicer_to_server(
        ArtistService(), server
    )
    
    # Add HealthServicer to the server.
    health_pb2_grpc.add_HealthServicer_to_server(
        HealthServicer(), server
    )
    server.add_insecure_port("[::]:50052")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
