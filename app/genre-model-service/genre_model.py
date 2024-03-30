import psycopg2
from psycopg2 import sql
from concurrent import futures
import grpc
import os
from grpc_interceptor import ExceptionToStatusInterceptor
from app_pb2 import (
    Genre,
    GetGenresListResponse,
    GetGenreResponse,
    DeleteGenreResponse,
    AddGenreResponse,
    GetGenreTrackResponse
)

import app_pb2_grpc
from grpc_interceptor.exceptions import NotFound, InvalidArgument

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

class GenreService(app_pb2_grpc.GenreServiceServicer):
    def GetGenresList(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Genres") 
            cur.execute(query)
            row = cur.fetchone()
            conn.commit()
            if rows:
                genres = []
                for row in rows:
                    genres.append(
                        Genre(
                            row[0],
                            row[1],
                            row[2],
                            row[3],
                            row[4],
                        )
                    )
                return GetGenresListResponse(genres)
            else:        
                raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def GetGenre(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Genres WHERE genre_id = %s;") 
            cur.execute(query, (request.genre_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return GetGenreResponse(
                    Genre(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                    )
                )
            raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
         
    def DeleteGenre(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Genres WHERE genre_id = %s;") 
            cur.execute(query, (request.genre_id,))
            row = cur.fetchone()
            if not (row is None):
                response = DeleteGenreResponse(
                    Genre(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                    )
                )
                query = sql.SQL("DELETE FROM Genres WHERE genre_id = %s;") 
                cur.execute(query, (request.genre_id,))
                conn.commit()
                return response
            raise NotFound()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def AddGenre(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL(
                "INSERT INTO Genres (genre_name, song_count, genre_url, updated_on) VALUES (%s,%s,%s,%s) RETURNING genre_id;") 
            cur.execute(query, (request.genre,))
            genre_id = cur.fetchone()[0]
            query = sql.SQL("SELECT * FROM Genres WHERE genre_id = %s;") 
            cur.execute(query, (genre_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return AddGenreResponse(
                    Genre(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                    )
                )
            raise InvalidArgument()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def GetGenreTrack(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL(
                "SELECT * FROM Genres WHERE genre_id = %s;")
            cur.execute(query, (request.genre_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return GetGenreTrackResponse(
                    Genre(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
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
    app_pb2_grpc.add_GenreServiceServicer_to_server(
        GenreService(), server
    )
    server.add_insecure_port("[::]:50055")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
