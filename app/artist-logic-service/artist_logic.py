from flask import Flask, jsonify
import grpc
import os
from app_pb2 import GetArtistRequest, AddArtistRequest, NewArtist, GetArtistReleasesIdsRequest, GetReleaseRequest, GetArtistTracksIdsRequest, GetTrackRequest 
from flask import request
from app_pb2_grpc import ArtistServiceStub, ArtistsReleasesServiceStub, ReleaseServiceStub, ArtistsTracksServiceStub, TrackServiceStub 

app = Flask(__name__)

artist_host = os.getenv("ARTIST_HOST", "localhost")
artists_channel = grpc.insecure_channel(f"{artist_host}:50052")
artist_client = ArtistServiceStub(artists_channel)

artists_releases_host = os.getenv("ARTISTS_RELEASES_HOST", "localhost")
artists_releases_channel = grpc.insecure_channel(f"{artists_releases_host}:50053")
artist_releases_client = ArtistsReleasesServiceStub(artists_releases_channel)

release_host = os.getenv("RELEASE_HOST", "localhost")
release_channel = grpc.insecure_channel(f"{release_host}:50058")
release_client = ReleaseServiceStub(release_channel)

track_host = os.getenv("TRACK_HOST", "localhost")
track_channel = grpc.insecure_channel(f"{track_host}:50051")
track_client = TrackServiceStub(track_channel)

artists_tracks_host = os.getenv("ARTISTS_TRACKS_HOST", "localhost")
artists_tracks_channel = grpc.insecure_channel(f"{artists_tracks_host}:50054")
artists_tracks_client = ArtistsTracksServiceStub(artists_tracks_channel)


@app.get("/api/artists/<int:artist_id>")
def get_artist(artist_id):
    try:
        request = GetArtistRequest(artist_id=artist_id)
        response = artist_client.getArtist(request)
        return {
            "artist_id": response.artist.artist_id,
            "artist_name": response.artist.artist_name,
            "artist_url": response.artist.artist_url
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Artist´s id not found", 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.post("/api/artists")
def add_artist():
    try:
        request_body = request.json
        add_request = AddArtistRequest(artist=NewArtist(
            artist_name=str(request_body['artist_name']),
            artist_url=str(request_body['artist_url']),
            artist_updated_at = str(request_body['artist_updated_at'])
        ))
        response = artist_client.addArtist(add_request)
        return {
            "artist_id": response.artist.artist_id,
            "artist_name": response.artist.artist_name,
            "artist_url": response.artist.artist_url
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.ALREADY_EXISTS:
            return rpc_error.details(), 403
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.get("/api/artists/<int:artist_id>/releases")
def getArtistReleases(artist_id):
    try:
        request = GetArtistReleasesIdsRequest(artist_id=artist_id)
        response = artist_releases_client.getArtistReleasesIds(request)
        releases = []
        for release_id in response.releases_ids:
            request = GetReleaseRequest(release_id=release_id)
            res = release_client.GetRelease(request)
            release = {
                "release_id": res.release.release_id,
                "release_title": res.release.release_title,
                "release_date": res.release.release_date,
                "release_url": res.release.release_url,
                "updated_on": res.release.updated_on
            }
            releases.append(release)
        return releases, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.get("/api/artists/<int:artist_id>/tracks")
def getArtistTracks(artist_id):
    try:
        request = GetArtistTracksIdsRequest(artist_id=artist_id)
        response = artists_tracks_client.getArtistTracks(request)
        tracks = []
        for track_id in response.tracks_ids:
            request = GetTrackRequest(track_id=track_id)
            res = track_client.getTrack(request)
            track = {
                "track_id": res.track.track.track.track_id,
                "title": res.track.track.title,
                "mix": res.track.track.mix,
                "is_remixed": res.track.track.is_remixed,
                "release_id": res.track.track.release_id,
                "release_date": res.track.track.release_date,
                "genre_id": res.track.track.genre_id,
                "subgenre_id": res.track.track.subgenre_id,
                "track_url": res.track.track.track_url,
                "bpm": res.track.track.bpm,
                "duration": res.track.track.duration
            }
            tracks.append(track)
        return tracks, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500
    
    
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200