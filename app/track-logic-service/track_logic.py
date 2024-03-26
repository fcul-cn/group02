from flask import Flask
import grpc
import os
from track_pb2 import GetTrackRequest, DeleteTrackRequest, AddTrackRequest, GetTrackGenreRequest
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
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Track´s id not found", 404
    
@app.delete("/api/tracks/<track_id>")
def delete_track(track_id):
    try:
        request = DeleteTrackRequest(track_id=int(track_id))
        response = track_client.deleteTrack(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Track´s id not found", 404

@app.post("/api/tracks")
def post_track():
    try:
        request_body = request.json
        request = AddTrackRequest(request_body)
        response = track_client.addTrack(request)
        return response
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
