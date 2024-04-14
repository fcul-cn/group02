import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import GetReleaseResponse, AddReleaseResponse, Release
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

class ReleaseService(app_pb2_grpc.ReleaseServiceServicer):
    def GetRelease(self, request, context):
        try:
            if request.release_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Release's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Releases WHERE release_id = %s;") 
            cur.execute(query, (request.release_id,))
            row = cur.fetchone()
            conn.commit()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Release not found.")
                context.abort()
            return GetReleaseResponse(release=Release(
                    release_id=row[0],
                    release_title=row[1],
                    release_date=str(row[2]),
                    release_url=row[3],
                    updated_on=str(row[4]),
                ))
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def AddRelease(self, request, context):
        check_if_title_exists = sql.SQL("SELECT 1 FROM Releases WHERE release_title = %s")
        check_if_url_exists = sql.SQL("SELECT 1 FROM Releases WHERE release_url = %s")
        try:
            if not request.release.release_title or not request.release.release_date or not request.release.release_url:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Release title, release date and url are required.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            cur.execute(check_if_title_exists, (request.release.release_title,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Release's title already exists.")
                context.abort()
            cur.execute(check_if_url_exists, (request.release.release_url,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Release's url already exists.")
                context.abort()
            query = sql.SQL("INSERT INTO Releases (release_title, release_date, release_url, updated_on) VALUES (%s,TO_DATE(%s, 'YYYY/MM/DD'),%s,CURRENT_DATE) RETURNING release_id;") 
            cur.execute(query, (request.release.release_title, request.release.release_date, request.release.release_url))
            release_id = cur.fetchone()[0]
            query = sql.SQL("SELECT * FROM Releases WHERE release_id = %s;") 
            cur.execute(query, (release_id,))
            row = cur.fetchone()
            conn.commit()
            return AddReleaseResponse(release=Release(
                    release_id=row[0],
                    release_title=row[1],
                    release_date=str(row[2]),
                    release_url=row[3],
                    updated_on=str(row[4]),
            ))
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
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
    app_pb2_grpc.add_ReleaseServiceServicer_to_server(
        ReleaseService(), server
    )
    
    # Add HealthServicer to the server.
    health_pb2_grpc.add_HealthServicer_to_server(
        HealthServicer(), server
    )
    
    server.add_insecure_port("[::]:50058")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
