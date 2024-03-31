from flask import Flask, request, jsonify
import grpc
import os
from app_pb2 import GetPlaylistRequest, DeletePlaylistRequest, AddPlaylistRequest, GetPlaylistTracksRequest, AddTrackToPlaylistRequest, DeleteTrackFromPlaylistRequest, NewPlaylist, GetTrackRequest
from app_pb2_grpc import PlaylistServiceStub, TrackServiceStub

app = Flask(__name__)

playlist_host = os.getenv("PLAYLIST_HOST", "localhost")
playlists_channel = grpc.insecure_channel(f"{playlist_host}:50057")
playlist_client = PlaylistServiceStub(playlists_channel)

track_host = os.getenv("TRACK_HOST", "localhost")
tracks_channel = grpc.insecure_channel(f"{track_host}:50051")
track_client = TrackServiceStub(tracks_channel)

@app.get("/api/playlists/<playlist_id>")
def get_playlist(playlist_id):
    try:
        request = GetPlaylistRequest(playlist_id=int(playlist_id))
        response = playlist_client.getPlaylist(request)
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
    
@app.delete("/api/playlists/<playlist_id>")
def delete_playlist(playlist_id):
    try:
        request = DeletePlaylistRequest(playlist_id=int(playlist_id))
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
        request_body = request.json
        add_request = AddPlaylistRequest(playlist=NewPlaylist(
            user_id=int(request_body['user_id']),
            playlist_name=request_body['playlist_name']
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
            return "Bad request body", 400
    except Exception as e:
        return "Internal error: " + str(e), 500

@app.get("/api/playlists/<playlist_id>/tracks")
def get_playlist_tracks(playlist_id):
    try:
        request = GetPlaylistTracksRequest(playlist_id=int(playlist_id))
        response = playlist_client.getPlaylistTracks(request)
        tracks_details = []
        
        for track_id in response.track_ids:
            request = GetTrackRequest(track_id=track_id)
            response = track_client.GetTrack(request)
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
        
@app.post("/api/playlists/<playlist_id>/tracks/<track_id>")
def post_track_to_playlist(playlist_id, track_id):
    try:
        request = AddTrackToPlaylistRequest(playlist_id=int(playlist_id), track_id=int(track_id))
        response = playlist_client.addTrackToPlaylist(request)
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
        
@app.get("/api/playlists/<playlist_id>/tracks/<track_id>")
def delete_track_from_playlist(playlist_id, track_id):
    try:
        request = DeleteTrackFromPlaylistRequest(playlist_id=int(playlist_id), track_id=int(track_id))
        response = playlist_client.deleteTrackFromPlaylist(request)
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
