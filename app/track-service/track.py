from flask import Flask

app = Flask(__name__)

@app.get("/api/tracks/<track_id>")
def get_track(track_id):
    
@app.delete("/api/tracks/<track_id>")
def delete_track(track_id):

@app.post("/api/tracks")
def post_track(track_id):