from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import (
    GetArtistReleasesIdsResponse,
    AddReleaseArtistsResponse
)
import app_pb2_grpc
from google.cloud import bigquery
from google.oauth2 import service_account
import json, os
import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2, health_pb2_grpc

json_string = os.environ.get('API_TOKEN')
project_id = os.environ.get('PROJECT_ID')
json_file = json.loads(json_string)
credentials = service_account.Credentials.from_service_account_info(json_file)
client = bigquery.Client(credentials=credentials, location="europe-west4")
table_id = f"{project_id}.ArtistsReleases"

class ArtistsReleasesService(app_pb2_grpc.ArtistsReleasesService):
    def getArtistReleasesIds(self, request, context):
        try:
            artist_id = request.artist_id
            if artist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Artist's id must be higher than 0.")
                context.abort()
            query = f"SELECT release_id FROM {table_id} WHERE artist_id = {artist_id}"
            query_job = client.query(query)
            result = query_job.result()
            rows = list(result)
            releases = []
            for row in rows:
                releases.append(int(row[0]))
            print(f"releases: {releases}")
            return GetArtistReleasesIdsResponse(releases_ids=releases)
        except Exception as e:
            print(f"Error: {e}")
    
    def addReleaseArtists(self, request, context):
        print(f"request: {request.artists_ids}")
        print(f"request: {request.release_id}")
        if request.release_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Release's id must be higher than 0.")
            context.abort()
        for artist_id in request.artists_ids:
            if artist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Artist's id must be higher than 0.")
                context.abort()
        for artist_id in request.artists_ids:
            query = f"SELECT 1 FROM {table_id} WHERE artist_id = {artist_id} AND release_id = {request.release_id};"
            query_job = client.query(query)
            result = query_job.result()
            if result.total_rows == 0:
                row_to_insert = [{u"artist_id": artist_id, u"release_id": request.release_id}]
                client.insert_rows_json(table_id, row_to_insert)
        return AddReleaseArtistsResponse()

class HealthServicer(health_pb2_grpc.HealthServicer):
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)

def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    app_pb2_grpc.add_ArtistsReleasesServiceServicer_to_server(
        ArtistsReleasesService(), server
    )
    
    # Add HealthServicer to the server.
    health_pb2_grpc.add_HealthServicer_to_server(
        HealthServicer(), server
    )
    
    server.add_insecure_port("[::]:50053")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
