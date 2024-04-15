from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import Track, GetTrackResponse, DeleteTrackResponse, AddTrackResponse, GetTrackGenreResponse, GetGenreTracksResponse
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
table_id = "confident-facet-329316.project.Tracks"

class TrackService(app_pb2_grpc.TrackServiceServicer):
    def getTrack(self, request, context):
        if request.track_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Track's id must be higher than 0.")
            context.abort()
        query = f"SELECT * FROM {table_id} WHERE track_id = {request.track_id};" 
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Track not found.")
            context.abort()
        row = list(result)[0]
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
         
    def deleteTrack(self, request, context):
        if request.track_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Track's id must be higher than 0.")
            context.abort()
        query = f"SELECT * FROM {table_id} WHERE track_id = {request.track_id};" 
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Track not found.")
            context.abort()
        row = list(result)[0]
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
        query = f"DELETE FROM {table_id} WHERE track_id = {request.track_id};"
        query_job = client.query(query)
        query_job.result()
        return response

    def addTrack(self, request, context):
        if request.track.genre_id <= 0 or request.track.subgenre_id <= 0 or request.track.release_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Genres's and Release's ids must be higher than 0.")
                context.abort()
        if not request.track.title or not request.track.mix or not request.track.release_date or not request.track.track_url:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Bad request body.")
            context.abort()
        check_if_title_exists = f"SELECT 1 FROM {table_id} WHERE title = \'{request.track.title}\'"
        query_job = client.query(check_if_title_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Track´s title already exists.")
            context.abort()
        check_if_mix_exists = f"SELECT 1 FROM {table_id} WHERE mix = \'{request.track.mix}\'"
        query_job = client.query(check_if_mix_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Track´s mix already exists.")
            context.abort()
        check_if_track_url_exists = f"SELECT 1 FROM {table_id} WHERE track_url = \'{request.track.track_url}\'"
        query_job = client.query(check_if_track_url_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Track´s URL already exists.")
            context.abort()
        getMaxId = f"SELECT MAX(track_id) FROM {table_id};"
        query_job = client.query(getMaxId)
        result = query_job.result()
        track_id = list(result)[0][0] + 1
        row_to_insert = [
            {u"track_id": track_id, u"title": request.track.title, u"mix": request.track.mix, u"is_remixed": request.track.is_remixed, u"release_id": request.track.release_id, u"release_date": request.track.release_date, u"genre_id": request.track.genre_id, u"subgenre_id": request.track.subgenre_id, u"track_url": request.track.track_url, u"bpm": request.track.bpm, u"duration": request.track.duration},
        ]
        client.insert_rows_json(table_id, row_to_insert)
        get_new_track = f"SELECT * FROM {table_id} WHERE track_id = {track_id};"
        query_job = client.query(get_new_track)
        result = query_job.result()
        row = list(result)[0]	
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

    def getTrackGenre(self, request, context):
        print(f"track_id: {request.track_id}")
        if request.track_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Track's id must be higher than 0.")
            context.abort()
        query = f"SELECT genre_id FROM {table_id} WHERE track_id = {request.track_id};"
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Track not found.")
            context.abort()
        row = list(result)[0]
        print(f"row: {row}")
        return GetTrackGenreResponse(genre_id=row[0])

    def getGenreTracks(self, request, context):
        print(f"genre_id: {request.genre_id}")
        query = f"SELECT * FROM {table_id} WHERE genre_id = {request.genre_id} LIMIT {request.limit} OFFSET {request.offset};"
        query_job = client.query(query)
        result = query_job.result()
        tracks = []
        rows = list(result)
        print(f"rows: {rows}")
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
