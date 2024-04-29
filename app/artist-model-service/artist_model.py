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
from google.cloud import bigquery
from google.oauth2 import service_account
import json, os

json_string = os.environ.get('API_TOKEN')
project_id = os.environ.get('PROJECT_ID')
json_file = json.loads(json_string)
credentials = service_account.Credentials.from_service_account_info(json_file)
client = bigquery.Client(credentials=credentials, location="europe-west4")
table_id = f"{project_id}.Artists"

class ArtistService(app_pb2_grpc.ArtistService):
    def getArtist(self, request, context):
        artist_id = request.artist_id
        if artist_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Artist's id must be higher than 0.")
            context.abort()
        query = f"SELECT * FROM {table_id} WHERE artist_id = {artist_id};"
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Artist not found.")
            context.abort()
        row = list(result)[0]
        return GetArtistResponse(artist=Artist(
                artist_id=row[0],
                artist_name=row[1],
                artist_url=row[2],
                artist_updated_at=str(row[3]),
            )
        )

    def addArtist(self, request, context):
        artist_name = request.artist.artist_name 
        artist_url = request.artist.artist_url
        if not artist_name or not artist_url:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Artist name and url are required.")
            context.abort()
        # Check if artist name or url already exist
        check_if_name_exists = f"SELECT 1 FROM {table_id} WHERE artist_name = \'{artist_name}\';"
        query_job = client.query(check_if_name_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Artist name already exists.")
            context.abort()

        check_if_url_exists = f"SELECT 1 FROM {table_id} WHERE artist_url = \'{artist_url}\';"
        query_job = client.query(check_if_url_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Artist URL already exists.")
            context.abort()

        getMaxId = f"SELECT MAX(artist_id) FROM {table_id};"
        query_job = client.query(getMaxId)
        result = query_job.result()
        artist_id = list(result)[0][0] + 1
        # Add artist
        row_to_insert = [
            {u"artist_id": artist_id, u"artist_name": artist_name, u"artist_url": artist_url, u"artist_updated_at": request.artist.artist_updated_at},
        ]
        client.insert_rows_json(table_id, row_to_insert)  # Make an API request.
        get_new_artist = f"SELECT * FROM {table_id} WHERE artist_id = {artist_id};"

        query_job = client.query(get_new_artist)
        result = query_job.result()
        row = list(result)[0]
        return AddArtistResponse(artist=Artist(
                artist_id=row[0],
                artist_name=row[1],
                artist_url=row[2],
                artist_updated_at=str(row[3]),
            )
        )


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
