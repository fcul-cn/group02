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
    AddGenreResponse,
    UpdateGenreResponse
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
            rows = cur.fetchall()
            conn.commit()
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
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

    def GetGenre(self, request, context):
        try:
            if request.genre_id <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Genre's id must be higher than 0.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Genres WHERE genre_id = %s;") 
            cur.execute(query, (request.genre_id,))
            row = cur.fetchone()
            conn.commit()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Genre not found.")
                context.abort()
            return GetGenreResponse(genre=
                Genre(
                    genre_id=row[0],
                    genre_name=row[1],
                    song_count=row[2],
                    genre_url=row[3],
                    updated_on=str(row[4]),
                )
            )
        except (psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
         
    def AddGenre(self, request, context):
        check_if_name_exists = sql.SQL("SELECT 1 FROM Genres WHERE genre_name = %s")
        check_if_url_exists = sql.SQL("SELECT 1 FROM Genres WHERE genre_url = %s")
        query = sql.SQL("INSERT INTO Genres (genre_name, song_count, genre_url, updated_on) VALUES (%s,0,%s,CURRENT_DATE) RETURNING genre_id;") 
        try:
            if not request.genre.genre_name or not request.genre.genre_url:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Bad request body.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            cur.execute(check_if_name_exists, (request.genre.genre_name,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Genre's name already exists.")
                context.abort()
            cur.execute(check_if_url_exists, (request.genre.genre_url,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Genre's url already exists.")
                context.abort()
            cur.execute(query, (request.genre.genre_name, request.genre.genre_url))
            genre_id = cur.fetchone()[0]
            query = sql.SQL("SELECT * FROM Genres WHERE genre_id = %s;") 
            cur.execute(query, (genre_id,))
            row = cur.fetchone()
            conn.commit()
            return AddGenreResponse(genre=
                Genre(
                    genre_id=row[0],
                    genre_name=row[1],
                    song_count=row[2],
                    genre_url=row[3],
                    updated_on=str(row[4]),
                )
            )
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def UpdateGenre(self, request, context):
        check_if_name_exists = sql.SQL("SELECT 1 FROM Genres WHERE genre_name = %s")
        check_if_url_exists = sql.SQL("SELECT 1 FROM Genres WHERE genre_url = %s")
        try:
            if not request.genre_name or not request.genre_url:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Bad request body.")
                context.abort()
            conn = connect()
            cur = conn.cursor()
            cur.execute(check_if_name_exists, (request.genre_name,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Genre's name already exists.")
                context.abort()
            cur.execute(check_if_url_exists, (request.genre_url,))
            if cur.fetchone():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Genre's url already exists.")
                context.abort()
            query = sql.SQL("UPDATE Genres SET genre_name=%s, genre_url=%s WHERE genre_id=%s;") 
            cur.execute(query, (request.genre_name, request.genre_url, request.genre_id))
            query = sql.SQL("SELECT * FROM Genres WHERE genre_id = %s;") 
            cur.execute(query, (request.genre_id,))
            row = cur.fetchone()
            if (row is None):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Genre not found.")
                context.abort()
            conn.commit()
            return UpdateGenreResponse(genre=
                Genre(
                    genre_id=row[0],
                    genre_name=row[1],
                    song_count=row[2],
                    genre_url=row[3],
                    updated_on=str(row[4]),
                )
            )
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
