from flask import Flask, request, jsonify
import grpc
import os
from app_pb2 import GetPlaylistRequest, DeletePlaylistRequest, AddPlaylistRequest, GetPlaylistTracksRequest, AddTrackToPlaylistRequest, DeleteTrackFromPlaylistRequest, NewPlaylist
from app_pb2_grpc import PlaylistServiceStub
import requests

app = Flask(__name__)

playlist_host = os.getenv("PLAYLIST_HOST", "localhost")
playlists_channel = grpc.insecure_channel(f"{playlist_host}:50057")
playlist_client = PlaylistServiceStub(playlists_channel)

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

@app.post("/api/playlists")
def post_playlist():
    try:
        request_body = request.json
        add_request = AddPlaylistRequest(playlist=NewPlaylist(
            user_id=request_body['title'],
            playlist_name=request_body['mix']
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

@app.get("/api/playlists/<playlist_id>/tracks")
def get_playlist_tracks(playlist_id):
    try:
        request = GetPlaylistTracksRequest(playlist_id=int(playlist_id))
        response = playlist_client.getPlaylistTracks(request)
        tracks_details = []
        
        for track_id in response.track_ids:
            track_response = requests.get(f"http://track-service/api/tracks/{track_id}") #I kinda dont know the url
            if track_response.status_code == 200:
                track_data = track_response.json()
                tracks_details.append(track_data)
            else:
                print(f"Failed to retrieve track with ID: {track_id}")

        return jsonify(tracks_details)
    
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Playlist's id not found", 404
        
@app.post("/api/playlists/<playlist_id>/tracks/<track_id>")
def post_track_to_playlist(playlist_id, track_id):
    try:
        request = AddTrackToPlaylistRequest(playlist_id=int(playlist_id), track_id=int(track_id))
        response = playlist_client.addTrackToPlaylist(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Playlist or track ID not found", 404
        
@app.get("/api/playlists/<playlist_id>/tracks/<track_id>")
def delete_track_from_playlist(playlist_id, track_id):
    try:
        request = DeleteTrackFromPlaylistRequest(playlist_id=int(playlist_id), track_id=int(track_id))
        response = playlist_client.deleteTrackFromPlaylist(request)
        return response
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return "Playlist or track ID not found", 404
