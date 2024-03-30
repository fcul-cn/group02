from flask import Flask
import grpc
import os
from app_pb2 import GetArtistRequest, AddArtistRequest, GetArtistReleasesRequest, NewArtist
from flask import request
from app_pb2_grpc import ArtistServiceStub

app = Flask(__name__)

artist_host = os.getenv("ARTIST_HOST", "localhost")
artists_channel = grpc.insecure_channel(f"{artist_host}:50052")
artist_client = ArtistServiceStub(artists_channel)

@app.get("/api/artists/<artist_id>")
def get_artist(artist_id):
    try:
        request = GetArtistRequest(artist_id=int(artist_id))
        response = artist_client.getArtist(request)
        return {
            "artist_id": response.artist.artist_id,
            "artist_name": response.artist.artist_name,
            "artist_url": response.artist.artist_url
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Artist´s id not found", 404

@app.post("/api/artists")
def add_artist():
    try:
        request_body = request.json
        add_request = AddArtistRequest( artist=NewArtist(
            artist_name=request_body['artist_name'],
            artist_url=request_body['artist_url'],
            artist_updated_at = request_body['artist_updated_at']
        ))
        response = artist_client.addArtist(add_request)
        return {
            "artist_id": response.artist.artist_id,
            "artist_name": response.artist.artist_name,
            "artist_url": response.artist.artist_url
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.IN:
            return "Something was wrong with your request", 400

@app.post("/api/artists/<artist_id>/releases")
def getArtistReleases(artist_id):
    request = GetArtistReleasesRequest(artist_id=artist_id)
    response = artist_client.getArtistReleases(request)
    return response

