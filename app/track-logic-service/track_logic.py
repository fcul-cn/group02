from flask import Flask
import grpc
import os
from track_pb2 import GetTrackRequest, DeleteTrackRequest, AddTrackRequest, GetTrackGenreRequest
from track_pb2_grpc import TrackServiceStub

app = Flask(__name__)

track_host = os.getenv("TRACK_HOST", "localhost")
tracks_channel = grpc.insecure_channel(f"{track_host}:50051")
track_client = TrackServiceStub(tracks_channel)

@app.get("/api/tracks/<track_id>")
def get_track(track_id):
    request = GetTrackRequest(track_id=track_id)
    response = track_client.getTrack(request)
    return response
    
@app.delete("/api/tracks/<track_id>")
def delete_track(track_id):
    request = DeleteTrackRequest(track_id=track_id)
    response = track_client.deleteTrack(request)
    return response

@app.post("/api/tracks")
def post_track():
    request_body = request.json
    request = AddTrackRequest(request_body)
    response = track_client.addTrack(request)
    return response

@app.get("/api/tracks/<track_id>/genre")
def get_track_genre(track_id):
    request = GetTrackGenreRequest(track_id=track_id)
    response = track_client.getTrackGenre(request)
    return response

if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)
