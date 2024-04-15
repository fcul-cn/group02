from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import (
    GetArtistTracksIdsResponse,
    AddTrackArtistsResponse
)
import app_pb2_grpc
from grpc_interceptor.exceptions import NotFound, InvalidArgument, AlreadyExists
from grpc_health.v1.health import HealthServicer
from grpc_health.v1 import health_pb2, health_pb2_grpc
from google.cloud import bigquery
from google.oauth2 import service_account
import json, os

json_string = os.environ.get('API_TOKEN')
json_file = json.loads(json_string)
credentials = service_account.Credentials.from_service_account_info(json_file)
client = bigquery.Client(credentials=credentials, location="europe-west4")
table_id = "confident-facet-329316.project.ArtistsTracks"

class ArtistsTracksService(app_pb2_grpc.ArtistsTracksService):
    def getArtistTracksIds(self, request, context):
        print("enter")
        artist_id = request.artist_id
        if artist_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Artist's id must be higher than 0.")
            context.abort()
        query = f"SELECT track_id FROM {table_id} WHERE artist_id = {artist_id}"
        query_job = client.query(query)
        result = query_job.result()
        rows = list(result)
        tracks = []
        for row in rows:
            tracks.append(int(row[0]))
        return GetArtistTracksIdsResponse(tracks_ids=tracks)
    
    def addTrackArtists(self, request, context):
        if request.track_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Track's id must be higher than 0.")
            context.abort()
        for artist_id in request.artists_ids:
            if artist_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Artist's id must be higher than 0.")
                context.abort()
        query = f"SELECT 1 FROM {table_id} WHERE artist_id = {artist_id} AND track_id = {request.track_id};"
        for artist_id in request.artists_ids:
            query_job = client.query(query)
            result = query_job.result()
            if result.total_rows == 0:
                row_to_insert = [{u"artist_id": artist_id, u"track_id": request.track_id}]
                client.insert_rows_json(table_id, row_to_insert)
        return AddTrackArtistsResponse()

class HealthServicer(health_pb2_grpc.HealthServicer):
    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)
        
def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    app_pb2_grpc.add_ArtistsTracksServiceServicer_to_server(
        ArtistsTracksService(), server
    )
    
     # Add HealthServicer to the server.
    health_pb2_grpc.add_HealthServicer_to_server(
        HealthServicer(), server
    )
    server.add_insecure_port("[::]:50054")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
