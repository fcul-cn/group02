from flask import Flask, request
import grpc
import os
from app_pb2 import AddGenreRequest, GetGenreRequest, DeleteGenreRequest, UpdateGenreRequest, GetGenreTracksRequest, GetGenresListRequest, NewGenre
from app_pb2_grpc import GenreServiceStub, TrackServiceStub

app = Flask(__name__)

genre_host = os.getenv("GENRE_HOST", "localhost")
genres_channel = grpc.insecure_channel(f"{genre_host}:50055")
genre_client = GenreServiceStub(genres_channel)

track_host = os.getenv("TRACK_HOST", "localhost")
tracks_channel = grpc.insecure_channel(f"{track_host}:50051")
track_client = TrackServiceStub(tracks_channel)

@app.get("/api/genres")
def get_genres():
    try:
        request = GetGenresListRequest()
        response = genre_client.GetGenresList(request)
        genres = []
        for genre in response.genres:
            genres.append({
                "genre_id": genre.genre_id,
                "genre_name": genre.genre_name,
                "song_count": genre.song_count,
                "genre_url": genre.genre_url,
                "updated_on": genre.updated_on
            })
        return genres, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.get("/api/genres/<genre_id>")
def get_genre(genre_id):
    try:
        request = GetGenreRequest(genre_id=int(genre_id))
        response = genre_client.GetGenre(request)
        return {
            "genre_id": response.genre.genre_id,
            "genre_name": response.genre.genre_name,
            "song_count": response.genre.genre_id,
            "genre_url": response.genre.song_count,
            "updated_on": response.genre.updated_on
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.post("/api/genres")
def post_genres():
    try:
        request_body = request.json
        post_request = AddGenreRequest(genre=NewGenre(
            genre_name=request_body['genre_name'],
            genre_url=request_body['genre_url']
        ))
        response = genre_client.AddGenre(post_request)
        return {
            "genre_id": response.genre.genre_id,
            "genre_name": response.genre.genre_name,
            "song_count": response.genre.genre_id,
            "genre_url": response.genre.song_count,
            "updated_on": response.genre.updated_on
        }, 201
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
        if rpc_error.code() == grpc.StatusCode.ALREADY_EXISTS:
            return rpc_error.details(), 403
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.delete("/api/genres/<genre_id>")
def delete_genre(genre_id):
    try:
        request = DeleteGenreRequest(genre_id=int(genre_id))
        response = genre_client.DeleteGenre(request)
        return {
            "genre_id": response.genre.genre_id,
            "genre_name": response.genre.genre_name,
            "song_count": response.genre.genre_id,
            "genre_url": response.genre.song_count,
            "updated_on": response.genre.updated_on
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.put("/api/genres/<genre_id>")
def update_genre(genre_id):
    try:
        request_body = request.json
        delete_request = UpdateGenreRequest(
            genre_id=int(genre_id),
            genre_name=request_body['genre_name'],
            genre_url=request_body['genre_url']
        )
        response = genre_client.UpdateGenre(delete_request)
        return {
            "genre_id": response.genre.genre_id,
            "genre_name": response.genre.genre_name,
            "song_count": response.genre.genre_id,
            "genre_url": response.genre.song_count,
            "updated_on": response.genre.updated_on
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.get("/api/genres/<genre_id>/tracks")
def get_genre_tracks(genre_id):
    try:
        request = GetGenreTracksRequest(genre_id=int(genre_id))
        response = track_client.getGenreTracks(request)
        tracks = []
        for track in response.track:
            tracks.append({
                "track_id": track.track_id,
                "title": track.title,
                "mix": track.mix,
                "is_remixed": track.is_remixed,
                "release_id": track.release_id,
                "release_date": track.release_date,
                "genre_id": track.genre_id,
                "subgenre_id": track.subgenre_id,
                "track_url": track.track_url,
                "bpm": track.bpm,
                "duration": track.duration
            })
        return tracks, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500
