import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import (
    GetArtistTracksIdsResponse,
    AddTrackArtistsResponse
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

class ArtistsTracksService(app_pb2_grpc.ArtistsTracksService):
    def getArtistTracksIds(self, request, context):
        try:
            artist_id = request.artist_id
            if artist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Artist's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT track_id FROM ArtistsTracks WHERE artist_id = %s")
            cur.execute(query, (artist_id,))
            rows = cur.fetchall()
            conn.commit()
            tracks = []
            for row in rows:
                tracks.append(row[0])
            return GetArtistTracksIdsResponse(tracks=tracks)
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
    
    def addTrackArtists(self, request, context):
        try:
            if request.track_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Track's id must be higher than 0.")
                context.abort()
            for artist_id in request.artists_ids:
                if artist_id <= 0:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Artist's id must be higher than 0.")
                    context.abort()
            conn = connect()
            cur = conn.cursor() 
            insert_query = sql.SQL("INSERT INTO ArtistsTracks VALUES (%s, %s);")
            query = sql.SQL("SELECT 1 FROM ArtistsTracks WHERE artist_id = %s AND track_id = %s;")
            for artist_id in request.artists_ids:
                cur.execute(query, (artist_id, request.track_id))
                if not cur.fetchone():
                    cur.execute(insert_query, (artist_id, request.track_id))
            conn.commit()
            return AddTrackArtistsResponse()
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
    app_pb2_grpc.add_ArtistsTracksServiceServicer_to_server(
        ArtistsTracksService(), server
    )
    server.add_insecure_port("[::]:50054")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
