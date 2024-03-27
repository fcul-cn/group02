from flask import Flask
import grpc
import os
from genre_pb2 import AddGenreRequest, GetGenreRequest, DeleteGenreRequest, UpdateGenreRequest, GetGenreTrackRequest, Empty
from genre_pb2_grpc import GenreServiceStub
import pathlib
import connexion

# basedir = pathlib.Path(__file__).parent.resolve()
# app = connexion.App(__name__, specification_dir=basedir)
# app.add_api(basedir / "openapi-group2.yaml")

app = Flask(__name__)

genre_host = os.getenv("GENRE_HOST", "localhost")
genres_channel = grpc.insecure_channel(f"{genre_host}:50051")
genre_client = GenreServiceStub(genress_channel)

@app.get("/api/genres")
def get_genres():
    try:
        request = GetGenreRequest(Empty)
        response = genre_client.GetGenresList(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Genres´s id not found", 404

@app.get("/api/genres/<genre_id>")
def get_genre(genre_id):
    try:
        request = GetGenreRequest(genre_id=int(genre_id))
        response = genre_client.GetGenre(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Genres´s id not found", 404

@app.post("/api/genres")
def post_genres():
    try:
        request_body = request.json
        request = AddGenreRequest(request_body)
        response = genre_client.AddGenre(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return "Bad request body", 400


@app.delete("/api/genres/<genres_id>")
def delete_genre(genre_id):
    try:
        request = DeleteGenreRequest(genre_id=int(genre_id))
        response = genre_client.DeleteGenre(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Genres´s id not found", 404


@app.put("/api/genres/<genres_id>")
def update_genre(genre_id):
    try:
        request = UpdateGenreRequest(genre_id=int(genre_id))
        response = genre_client.UpdateGenre(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Genres´s id not found", 404


@app.get("/api/genres/<genre_id>/tracks")
def get_genre_track(genre_id):
    try:
        request = GetGenreTrackRequest(genre_id=int(genre_id))
        response = genre_client.GetGenreTrack(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Genres´s id not found", 404
