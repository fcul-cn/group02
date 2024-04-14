from flask import Flask, request, jsonify
import grpc
import os
from app_pb2 import GetTrackRequest, DeleteTrackRequest, AddTrackRequest, GetTrackGenreRequest, NewTrack, GetGenreRequest, DeleteTrackFromPlaylistsRequest, GetReleaseRequest, AddTrackArtistsRequest
from app_pb2_grpc import TrackServiceStub, GenreServiceStub, PlaylistServiceStub, ReleaseServiceStub, ArtistsTracksServiceStub

app = Flask(__name__)

track_host = os.getenv("TRACK_HOST", "localhost")
tracks_channel = grpc.insecure_channel(f"{track_host}:50051")
track_client = TrackServiceStub(tracks_channel)

genre_host = os.getenv("GENRE_HOST", "localhost")
genres_channel = grpc.insecure_channel(f"{genre_host}:50055")
genre_client = GenreServiceStub(genres_channel)

playlist_host = os.getenv("PLAYLIST_HOST", "localhost")
playlists_channel = grpc.insecure_channel(f"{playlist_host}:50057")
playlist_client = PlaylistServiceStub(playlists_channel)

release_host = os.getenv("RELEASE_HOST", "localhost")
release_channel = grpc.insecure_channel(f"{release_host}:50058")
release_client = ReleaseServiceStub(release_channel)

artists_tracks_host = os.getenv("ARTISTS_TRACKS_HOST", "localhost")
artists_tracks_channel = grpc.insecure_channel(f"{artists_tracks_host}:50054")
artists_tracks_client = ArtistsTracksServiceStub(artists_tracks_channel)

@app.get("/api/tracks/<int:track_id>")
def get_track(track_id):
    try:
        request = GetTrackRequest(track_id=track_id)
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
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500
    
@app.delete("/api/tracks/<int:track_id>")
def delete_track(track_id):
    try:
        request = DeleteTrackFromPlaylistsRequest(track_id=track_id)
        playlist_client.deleteTrackFromPlaylists(request)
        request = DeleteTrackRequest(track_id=track_id)
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
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.post("/api/tracks")
def post_track():
    try:
        request_body = request.json
        get_genre_request = GetGenreRequest(genre_id=int(request_body['genre_id']))
        genre_client.GetGenre(get_genre_request)
        get_sub_genre_request = GetGenreRequest(genre_id=int(request_body['subgenre_id']))
        genre_client.GetGenre(get_sub_genre_request)
        get_release_request = GetReleaseRequest(release_id=int(request_body['release_id']))
        release_client.GetRelease(get_release_request)
        artists_tracks_channel.addTrackArtists(AddTrackArtistsRequest(track_id=response.track.track_id, artists_ids=request_body['artists_ids']))
        add_request = AddTrackRequest(track=NewTrack(
            title=str(request_body['title']),
            mix=str(request_body['mix']),
            is_remixed=bool(request_body['is_remixed']),
            release_id=int(request_body['release_id']),
            release_date=str(request_body['release_date']),
            genre_id=int(request_body['genre_id']),
            subgenre_id=int(request_body['subgenre_id']),
            track_url=str(request_body['track_url']),
            bpm=int(request_body['bpm']),
            duration=int(request_body['duration'])
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
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
        if rpc_error.code() == grpc.StatusCode.ALREADY_EXISTS:
            return rpc_error.details(), 403
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.get("/api/tracks/<int:track_id>/genre")
def get_track_genre(track_id):
    try:
        request = GetTrackGenreRequest(track_id=track_id)
        response = track_client.getTrackGenre(request)
        genre_id = response.genre_id
        request = GetGenreRequest(genre_id=genre_id)
        response = genre_client.GetGenre(request)
        return {
            "genre_id": response.genre.genre_id,
            "genre_name": response.genre.genre_name,
            "song_count": response.genre.song_count,
            "genre_url": response.genre.genre_url,
            "updated_on": response.genre.updated_on
        }, 200
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