import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import (
    GetArtistReleasesIdsResponse,
    AddReleaseArtistsResponse
)
import app_pb2_grpc

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

class ArtistsReleasesService(app_pb2_grpc.ArtistsReleasesService):
    def getArtistReleasesIds(self, request, context):
        try:
            artist_id = request.artist_id
            if artist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Artist's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT release_id FROM ArtistsReleases WHERE artist_id = %s")
            cur.execute(query, (artist_id,))
            rows = cur.fetchall()
            conn.commit()
            releases = []
            for row in rows:
                releases.append(row[0])
            return GetArtistReleasesIdsResponse(releases_ids=releases)
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
    
    def addReleaseArtists(self, request, context):
        try:
            if request.release_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Release's id must be higher than 0.")
                context.abort()
            for artist_id in request.artists_ids:
                if artist_id <= 0:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Artist's id must be higher than 0.")
                    context.abort()
            conn = connect()
            cur = conn.cursor() 
            insert_query = sql.SQL("INSERT INTO ArtistsReleases VALUES (%s, %s);")
            query = sql.SQL("SELECT 1 FROM ArtistsReleases WHERE artist_id = %s AND release_id = %s;")
            for artist_id in request.artists_ids:
                cur.execute(query, (artist_id, request.release_id))
                if not cur.fetchone():
                    cur.execute(insert_query, (artist_id, request.release_id))
            conn.commit()
            return AddReleaseArtistsResponse()
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
    app_pb2_grpc.add_ArtistsReleasesServiceServicer_to_server(
        ArtistsReleasesService(), server
    )
    server.add_insecure_port("[::]:50053")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
