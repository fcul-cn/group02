from flask import Flask, request, jsonify
import grpc
import os
from app_pb2 import GetPlaylistRequest, DeletePlaylistRequest, AddPlaylistRequest, GetPlaylistTracksRequest, UpdatePlaylistRequest, NewPlaylist, GetTrackRequest
from app_pb2_grpc import PlaylistServiceStub, TrackServiceStub
from prometheus_client import start_http_server, Histogram

app = Flask(__name__)

# Start up the server to expose the metrics.
start_http_server(5003)
histogram = Histogram('python_my_histogram', 'This is my histogram')

playlist_host = os.getenv("PLAYLIST_HOST", "localhost")
playlists_channel = grpc.insecure_channel(f"{playlist_host}:50057")
playlist_client = PlaylistServiceStub(playlists_channel)

track_host = os.getenv("TRACK_HOST", "localhost")
tracks_channel = grpc.insecure_channel(f"{track_host}:50051")
track_client = TrackServiceStub(tracks_channel)

@app.get("/api/playlists/<int:playlist_id>")
def get_playlist(playlist_id):
    try:
        with histogram.time():
            request = GetPlaylistRequest(playlist_id=playlist_id)
            response = playlist_client.getPlaylist(request)
            return {
                "playlist_id": response.playlist.playlist_id,
                "user_id": response.playlist.user_id,
                "playlist_name": response.playlist.playlist_name,
                "date_created": response.playlist.date_created
            }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500
    
@app.delete("/api/playlists/<int:playlist_id>")
def delete_playlist(playlist_id):
    try:
        with histogram.time():
            request = DeletePlaylistRequest(playlist_id=playlist_id)
            response = playlist_client.deletePlaylist(request)
            return {
                "playlist_id": response.playlist.playlist_id,
                "user_id": response.playlist.user_id,
                "playlist_name": response.playlist.playlist_name,
                "date_created": response.playlist.date_created
            }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Playlist's id not found", 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.post("/api/playlists")
def post_playlist():
    try:
        with histogram.time():
            request_body = request.json
            add_request = AddPlaylistRequest(playlist=NewPlaylist(
                user_id=int(request_body['user_id']),
                playlist_name=str(request_body['playlist_name'])
            ))
            response = playlist_client.addPlaylist(add_request)
            return {
                "playlist_id": response.playlist.playlist_id,
                "user_id": response.playlist.user_id,
                "playlist_name": response.playlist.playlist_name,
                "date_created": response.playlist.date_created
            }, 201   
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.get("/api/playlists/<int:playlist_id>/tracks")
def get_playlist_tracks(playlist_id):
    try:
        with histogram.time():
            request = GetPlaylistTracksRequest(playlist_id=playlist_id)
            response = playlist_client.getPlaylistTracks(request)
            tracks_details = []
            
            for track_id in response.track_ids:
                request = GetTrackRequest(track_id=track_id)
                response = track_client.getTrack(request)
                track_detail = {
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
                }
                tracks_details.append(track_detail)
            return tracks_details, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500
        
@app.put("/api/playlists/<int:playlist_id>/tracks")
def update_playlist_tracks(playlist_id):
    try:
        with histogram.time():
            request_body = request.json
            tracks_to_add=request_body["add"]
            tracks_to_delete=request_body["delete"]
            for track_id in tracks_to_add:
                get_request = GetTrackRequest(track_id=track_id)
                track_client.getTrack(get_request)
            for track_id in tracks_to_delete:
                get_request = GetTrackRequest(track_id=track_id)
                track_client.getTrack(get_request)
            update_request = UpdatePlaylistRequest(playlist_id=playlist_id, add_tracks_ids=tracks_to_add, delete_tracks_ids=tracks_to_delete)
            response = playlist_client.updatePlaylistTracks(update_request)
            return {
                "playlist_id": response.playlist.playlist_id,
                "user_id": response.playlist.user_id,
                "playlist_name": response.playlist.playlist_name,
                "date_created": response.playlist.date_created
            }, 201
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