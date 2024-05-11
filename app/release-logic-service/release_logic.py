from flask import Flask, request, jsonify
import grpc
import os
from app_pb2 import GetReleaseRequest, AddReleaseRequest, NewRelease, GetArtistRequest, AddReleaseArtistsRequest
from app_pb2_grpc import ReleaseServiceStub, ArtistServiceStub, ArtistsReleasesServiceStub

app = Flask(__name__)

release_host = os.getenv("RELEASE_HOST", "localhost")
release_channel = grpc.insecure_channel(f"{release_host}:50058")
release_client = ReleaseServiceStub(release_channel)

artist_host = os.getenv("ARTIST_HOST", "localhost")
artists_channel = grpc.insecure_channel(f"{artist_host}:50052")
artist_client = ArtistServiceStub(artists_channel)

artist_release_host = os.getenv("ARTIST_RELEASE_HOST", "localhost")
artist_release_channel = grpc.insecure_channel(f"{artist_release_host}:50053")
artist_release_client = ArtistsReleasesServiceStub(artist_release_channel)

@app.get("/api/releases/<int:release_id>")
def get_release(release_id):
    try:
        request = GetReleaseRequest(release_id=release_id)
        response = release_client.GetRelease(request)
        return {
            "release_id": response.release.release_id,
            "release_title": response.release.release_title,
            "release_date": response.release.release_date,
            "release_url": response.release.release_url,
            "updated_on": response.release.updated_on
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500
    
@app.post("/api/releases")
def post_releases():
    try:
        request_body = request.json
        for artist_id in request_body['artists_ids']:
            get_request = GetArtistRequest(artist_id=artist_id)
            artist_client.getArtist(get_request)
        add_request = AddReleaseRequest(release=NewRelease(
            release_title=str(request_body['release_title']),
            release_url=str(request_body['release_url']),
            release_date=str(request_body['release_date'])
        ))
        response = release_client.AddRelease(add_request)
        artist_release_client.addReleaseArtists(AddReleaseArtistsRequest(release_id=response.release.release_id, artists_ids=request_body['artists_ids']))
        return {
            "release_id": response.release.release_id,
            "release_title": response.release.release_title,
            "release_date": response.release.release_date,
            "release_url": response.release.release_url,
            "updated_on": response.release.updated_on
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200