from concurrent import futures
from datetime import datetime
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import (
    Genre,
    GetGenresListResponse,
    GetGenreResponse,
    AddGenreResponse,
    UpdateGenreResponse
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
table_id = f"{project_id}.Genres"

class GenreService(app_pb2_grpc.GenreServiceServicer):
    def GetGenresList(self, request, context):
        query = f"SELECT * FROM {table_id}" 
        query_job = client.query(query)
        result = query_job.result()
        rows = list(result)
        genres = []
        for row in rows:
            genres.append(
                Genre(
                    genre_id=row[0],
                    genre_name=row[1],
                    song_count=row[2],
                    genre_url=row[3],
                    updated_on=str(row[4]),
                )
            )
        return GetGenresListResponse(genres=genres)

    def GetGenre(self, request, context):
        if request.genre_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Genre's id must be higher than 0.")
            context.abort()
        query = f"SELECT * FROM {table_id} WHERE genre_id = {request.genre_id};" 
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Genre not found.")
            context.abort()
        row = list(result)[0]
        return GetGenreResponse(genre=
            Genre(
                genre_id=row[0],
                genre_name=row[1],
                song_count=row[2],
                genre_url=row[3],
                updated_on=str(row[4]),
            )
        )

    def AddGenre(self, request, context):
        if not request.genre.genre_name or not request.genre.genre_url:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Bad request body.")
            context.abort()
        check_if_name_exists = f"SELECT 1 FROM {table_id} WHERE genre_name = \'{request.genre.genre_name}\';"
        query_job = client.query(check_if_name_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Genre's name already exists.")
            context.abort()
        check_if_url_exists = f"SELECT 1 FROM {table_id} WHERE genre_url = \'{request.genre.genre_url}\';"
        query_job = client.query(check_if_url_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Genre's url already exists.")
            context.abort()

        getMaxId = f"SELECT MAX(genre_id) FROM {table_id};"
        query_job = client.query(getMaxId)
        result = query_job.result()
        genre_id = list(result)[0][0] + 1
        row_to_insert = [
            {u"genre_id": genre_id, u"genre_name": request.genre.genre_name, u"song_count": 0, u"genre_url": request.genre.genre_url, u"updated_on": datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        ]
        errors = client.insert_rows_json(table_id, row_to_insert)
        query = f"SELECT * FROM {table_id} WHERE genre_id = {genre_id};"
        query_job = client.query(query)
        result = query_job.result()
        row = list(result)[0]
        return AddGenreResponse(genre=
            Genre(
                genre_id=row[0],
                genre_name=row[1],
                song_count=row[2],
                genre_url=row[3],
                updated_on=str(row[4]),
            )
        )

    def UpdateGenre(self, request, context):
        print("Entered UpdateGenre")
        if not request.genre_name or not request.genre_url:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Bad request body.")
            context.abort()
        check_if_name_exists = f"SELECT 1 FROM {table_id} WHERE genre_name = \'{request.genre_name}\';"
        query_job = client.query(check_if_name_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Genre's name already exists.")
            context.abort()
        print("Checked name")
        check_if_url_exists = f"SELECT 1 FROM {table_id} WHERE genre_url = \'{request.genre_url}\';"
        query_job = client.query(check_if_url_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Genre's url already exists.")
            context.abort()
        print("Checked url")
        query = f"UPDATE {table_id} SET genre_name=\'{request.genre_name}\', genre_url=\'{request.genre_url}\' WHERE genre_id={request.genre_id};"
        query_job = client.query(query)
        query_job.result()
        print("Updated")
        query = f"SELECT * FROM {table_id} WHERE genre_id = {request.genre_id};"
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Genre not found.")
            context.abort()
        row = list(result)[0]
        return UpdateGenreResponse(genre=
            Genre(
                genre_id=row[0],
                genre_name=row[1],
                song_count=row[2],
                genre_url=row[3],
                updated_on=str(row[4]),
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
    app_pb2_grpc.add_GenreServiceServicer_to_server(
        GenreService(), server
    )
    # Add HealthServicer to the server.
    health_pb2_grpc.add_HealthServicer_to_server(
        HealthServicer(), server
    )
    server.add_insecure_port("[::]:50055")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
