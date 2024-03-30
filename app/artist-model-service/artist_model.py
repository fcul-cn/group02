import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from artist_pb2 import (
    Artist,
    GetArtistResponse,
    AddArtistResponse,
    GetArtistReleasesResponse,
)
import artist_pb2_grpc
from grpc_interceptor.exceptions import NotFound, InvalidArgument, AlreadyExists

def connect():
    try:
        print("Connecting to the PostgreSQL database...")
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

class ArtistService(artist_pb2_grpc.ArtistService):
    def getArtist(self, request, context):
        try:
            artist_id = request.artist_id
            print("artist_id: ", artist_id)
            if artist_id <= 0:
                raise InvalidArgument()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Artist WHERE artist_id = %s")
            cur.execute(query, (artist_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return GetArtistResponse(artist=Artist(
                        artist_id=row[0],
                        artist_name=row[1],
                        artist_url=row[2],
                        artist_updated_at=str(row[3]),
                    )
                )
            raise NotFound()
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
                raise InvalidArgument()
            conn = connect()
            cur = conn.cursor()
            # Check if artist name or url already exists
            cur.execute(check_if_name_exists, (artist_name,))
            if cur.fetchone():
                raise AlreadyExists()
            cur.execute(check_if_url_exists, (artist_url,))
            if cur.fetchone():
                raise AlreadyExists()
            # Add artist
            cur.execute(query, (artist_name, artist_url, request.artist.artist_updated_at))
            artist_id = cur.fetchone()[0]
            cur.execute(get_new_artist, (artist_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return AddArtistResponse(artist=Artist(
                        artist_id=row[0],
                        artist_name=row[1],
                        artist_url=row[2],
                        artist_updated_at=str(row[3]),
                    )
                )
            raise InvalidArgument()
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
    
    def getArtistReleases(self, request, context):
        return GetArtistReleasesResponse() 



def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    artist_pb2_grpc.add_ArtistServiceServicer_to_server(
        ArtistService(), server
    )
    server.add_insecure_port("[::]:50052")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
