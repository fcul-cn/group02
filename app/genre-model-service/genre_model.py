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
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("SELECT * FROM Genres WHERE genre_id = %s;") 
            cur.execute(query, (request.genre_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return GetGenreResponse(genre=
                    Genre(
                        genre_id=row[0],
                        genre_name=row[1],
                        song_count=row[2],
                        genre_url=row[3],
                        updated_on=str(row[4]),
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
                response = DeleteGenreResponse(genre=
                    Genre(
                        genre_id=row[0],
                        genre_name=row[1],
                        song_count=row[2],
                        genre_url=row[3],
                        updated_on=str(row[4]),
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
            query = sql.SQL("INSERT INTO Genres (genre_name, song_count, genre_url, updated_on) VALUES (%s,0,%s,CURRENT_DATE) RETURNING genre_id;") 
            cur.execute(query, (request.genre.genre_name, request.genre.genre_url))
            genre_id = cur.fetchone()[0]
            query = sql.SQL("SELECT * FROM Genres WHERE genre_id = %s;") 
            cur.execute(query, (genre_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return AddGenreResponse(genre=
                    Genre(
                        genre_id=row[0],
                        genre_name=row[1],
                        song_count=row[2],
                        genre_url=row[3],
                        updated_on=str(row[4]),
                    )
                )
            raise InvalidArgument()
        except (psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            if conn is not None:
                conn.close()

    def UpdateGenre(self, request, context):
        try:
            conn = connect()
            cur = conn.cursor()
            query = sql.SQL("UPDATE Genres SET genre_name=%s, genre_url=%s WHERE genre_id=%s;") 
            cur.execute(query, (request.genre_name, request.genre_url, request.genre_id))
            query = sql.SQL("SELECT * FROM Genres WHERE genre_id = %s;") 
            cur.execute(query, (request.genre_id,))
            row = cur.fetchone()
            conn.commit()
            if not (row is None):
                return UpdateGenreResponse(genre=
                    Genre(
                        genre_id=row[0],
                        genre_name=row[1],
                        song_count=row[2],
                        genre_url=row[3],
                        updated_on=str(row[4]),
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
