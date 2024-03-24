from flask import Flask
import grpc
from track_pb2 import GetTrackRequest
from track_pb2_grpc import TrackServiceStub

app = Flask(__name__)

@app.get("/api/tracks/<track_id>")
def get_track(track_id):
    request = GetTrackRequest(track_id=track_id)
    response = TrackModelService.getTrack(request)
    return response
    
#@app.delete("/api/tracks/<track_id>")
#def delete_track(track_id):

#@app.post("/api/tracks")
#def post_track(track_id):