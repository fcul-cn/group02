import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import Track, GetReleaseResponse, DeleteReleaseResponse, AddReleaseResponse
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

class ReleaseService(app_pb2_grpc.ReleaseServiceServicer):
    def GetRelease(self, request, context):
        try:
            if request.release_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Release's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Release WHERE release_id = %s;") 
            cur.execute(query, (request.release_id,))
            row = cur.fetchone()
            conn.commit()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Release not found.")
                context.abort()
            return GetReleaseResponse(release=Release(
                    release_id=row[0],
                    title=row[1],
                    date=row[2],
                    url=row[3],
                    updated_on=row[4],
                ))
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
         
    def DeleteRelease(self, request, context):
        try:
            if request.release_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Release's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Release WHERE release_id = %s;") 
            cur.execute(query, (request.release_id,))
            row = cur.fetchone()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Release not found.")
                context.abort()
            response = DeleteReleaseResponse(release=Release(
                    release_id=row[0],
                    title=row[1],
                    date=row[2],
                    url=row[3],
                    updated_on=row[4],
                )
            )
            query = sql.SQL("DELETE FROM Release WHERE release_id = %s;") 
            cur.execute(query, (request.release_id,))
            conn.commit()
            return response
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def AddRelease(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("INSERT INTO Release (title, date, url, updated_on) VALUES (%s,%s,%s,CURRENT_DATE) RETURNING release_id;") 
            cur.execute(query, (request.release.title, request.release.date, request.release.url))
            release_id = cur.fetchone()[0]
            query = sql.SQL("SELECT * FROM Release WHERE release_id = %s;") 
            cur.execute(query, (release_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return AddReleaseResponse(release=
                    Release(
                        release_id=row[0],
                        title=row[1],
                        date=row[2],
                        url=row[3],
                        updated_on=row[4],
                    )
                )
            raise InvalidArgument()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

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
