from flask import Flask, request
import grpc
import os
from track_pb2 import GetTrackRequest, DeleteTrackRequest, AddTrackRequest, GetTrackGenreRequest, NewTrack
from track_pb2_grpc import TrackServiceStub
import pathlib
import connexion

# basedir = pathlib.Path(__file__).parent.resolve()
# app = connexion.App(__name__, specification_dir=basedir)
# app.add_api(basedir / "openapi-group2.yaml")

app = Flask(__name__)

track_host = os.getenv("TRACK_HOST", "localhost")
tracks_channel = grpc.insecure_channel(f"{track_host}:50051")
track_client = TrackServiceStub(tracks_channel)

@app.get("/api/tracks/<track_id>")
def get_track(track_id):
    try:
        request = GetTrackRequest(track_id=int(track_id))
        response = track_client.getTrack(request)
        return {
            "track_id": response.track.track_id,
            "title": response.track.title,
            "mix": response.track.mix,
            "is_remixed": response.track.is_remixed,
            "release_id": response.track.release_id,
            "release_date": response.track.release_date,
            "genre_id": response.track.genre_id,
            "subgenre_id": response.track.subgenre_id,
            "track_url": response.track.track_url,
            "bpm": response.track.bpm,
            "duration": response.track.duration
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Track´s id not found", 404
    
@app.delete("/api/tracks/<track_id>")
def delete_track(track_id):
    try:
        request = DeleteTrackRequest(track_id=int(track_id))
        response = track_client.deleteTrack(request)
        return {
            "track_id": response.track.track_id,
            "title": response.track.title,
            "mix": response.track.mix,
            "is_remixed": response.track.is_remixed,
            "release_id": response.track.release_id,
            "release_date": response.track.release_date,
            "genre_id": response.track.genre_id,
            "subgenre_id": response.track.subgenre_id,
            "track_url": response.track.track_url,
            "bpm": response.track.bpm,
            "duration": response.track.duration
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Track´s id not found", 404

@app.post("/api/tracks")
def post_track():
    try:
        request_body = request.json
        add_request = AddTrackRequest(track=NewTrack(
            title=request_body['title'],
            mix=request_body['mix'],
            is_remixed=request_body['is_remixed'],
            release_id=request_body['release_id'],
            release_date=request_body['release_date'],
            genre_id=request_body['genre_id'],
            subgenre_id=request_body['subgenre_id'],
            track_url=request_body['track_url'],
            bpm=request_body['bpm'],
            duration=request_body['duration']
        ))
        response = track_client.addTrack(add_request)
        return {
            "track_id": response.track.track_id,
            "title": response.track.title,
            "mix": response.track.mix,
            "is_remixed": response.track.is_remixed,
            "release_id": response.track.release_id,
            "release_date": response.track.release_date,
            "genre_id": response.track.genre_id,
            "subgenre_id": response.track.subgenre_id,
            "track_url": response.track.track_url,
            "bpm": response.track.bpm,
            "duration": response.track.duration
        }, 201   
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return "Bad request body", 400

@app.get("/api/tracks/<track_id>/genre")
def get_track_genre(track_id):
    try:
        request = GetTrackGenreRequest(track_id=int(track_id))
        response = track_client.getTrackGenre(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Track´s id not found", 404
