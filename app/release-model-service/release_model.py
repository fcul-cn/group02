from concurrent import futures
from datetime import datetime
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import GetReleaseResponse, AddReleaseResponse, Release
import app_pb2_grpc
from google.cloud import bigquery
from google.oauth2 import service_account
import json, os

json_string = os.environ.get('API_TOKEN')
json_file = json.loads(json_string)
credentials = service_account.Credentials.from_service_account_info(json_file)
client = bigquery.Client(credentials=credentials, location="europe-west4")
table_id = "confident-facet-329316.project.Releases"

class ReleaseService(app_pb2_grpc.ReleaseServiceServicer):
    def GetRelease(self, request, context):
        if request.release_id <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Release's id must be higher than 0.")
            context.abort()
        query = f"SELECT * FROM {table_id} WHERE release_id={request.release_id};"
        query_job = client.query(query)
        result = query_job.result()
        if result.total_rows == 0:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Release not found.")
            context.abort()
        row = list(result)[0]
        return GetReleaseResponse(release=Release(
                release_id=row[0],
                release_title=row[1],
                release_date=str(row[2]),
                release_url=row[3],
                updated_on=str(row[4]),
            ))

    def AddRelease(self, request, context):
        if not request.release.release_title or not request.release.release_date or not request.release.release_url:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Release title, release date and url are required.")
            context.abort()
        check_if_title_exists = f"SELECT 1 FROM {table_id} WHERE release_title = {request.release.release_title}"
        query_job = client.query(check_if_title_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Release's title already exists.")
            context.abort()
        check_if_url_exists = f"SELECT 1 FROM {table_id} WHERE release_url = {request.release.release_url}"
        query_job = client.query(check_if_name_exists)
        result = query_job.result()
        if result.total_rows != 0:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Release's url already exists.")
            context.abort()

        getMaxId = f"SELECT MAX(release_id) FROM {table_id};"
        query_job = client.query(getMaxId)
        result = query_job.result()
        release_id = list(result)[0][0] + 1

        row_to_insert = [
            {u"release_title":request.release.release_title, u"release_date":request.release.release_date, u"release_url":request.release.release_url, u"updated_on":datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        ]
        client.insert_rows_json(table_id, row_to_insert)

        query = f"SELECT * FROM {table_id} WHERE release_id = {release_id};" 
        query_job = client.query(get_new_artist)
        result = query_job.result()
        row = list(result)[0]
        return AddReleaseResponse(release=Release(
                release_id=row[0],
                release_title=row[1],
                release_date=str(row[2]),
                release_url=row[3],
                updated_on=str(row[4]),
        ))

def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    app_pb2_grpc.add_ReleaseServiceServicer_to_server(
        ReleaseService(), server
    )
    server.add_insecure_port("[::]:50058")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
