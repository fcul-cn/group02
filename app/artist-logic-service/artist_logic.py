from flask import Flask
import grpc
import os
from artist_pb2 import GetArtistRequest, AddArtistRequest, GetArtistReleasesRequest
from artist_pb2_grpc import ArtistServiceStub

app = Flask(__name__)

artist_host = os.getenv("ARTIST_HOST", "localhost")
artists_channel = grpc.insecure_channel(f"{artist_host}:50051")
artist_client = ArtistServiceStub(artists_channel)

@app.get("/api/artists/<artist_id>")
def get_artist(artist_id):
    request = GetArtistRequest(artist_id=artist_id)
    response = artist_client.getArtist(request)
    return response

@app.post("/api/artists")
def add_artist(artist_id):
    request_body = request.json
    request = AddArtistRequest(artist_name = request_body.artist_name, artist_url = request_body.artist_url)
    response = artist_client.addArtist(request)
    return response

@app.post("/api/artists/<artist_id>/releases")
def add_artist(artist_id):
    request = GetArtistReleasesRequest(artist_id=artist_id)
    response = artist_client.getArtistReleases(request)
    return response

if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)
