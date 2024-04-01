from flask import Flask, request
import grpc
import os
from app_pb2 import GetReleaseRequest, DeleteReleaseRequest, AddReleaseRequest
from app_pb2_grpc import ReleaseServiceStub, ReleaseServiceStub

app = Flask(__name__)

release_host = os.getenv("RELEASE_HOST", "localhost")
release_channel = grpc.insecure_channel(f"{release_host}:50058")
release_client = ReleaseServiceStub(release_channel)

@app.get("/api/releases/<int:release_id>")
def get_release(release_id):
    try:
        request = GetReleaseRequest(release_id=release_id)
        response = release_client.GetRelease(request)
        return {
            "release_id": response.release.release_id,
            "title": response.release.title,
            "date": response.release.date,
            "url": response.release.url,
            "updated_on": response.release.updated_on,
        }, 200
    except grpc.RpcError as rpc_error:
        if rpc_error.code() == grpc.StatusCode.NOT_FOUND:
            return rpc_error.details(), 404
        if rpc_error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            return rpc_error.details(), 400
    except Exception as e:
        return "Internal error: " + str(e), 500
    
@app.delete("/api/releases/<int:release_id>")
def delete_release(release_id):
    try:
        request = DeleteReleaseRequest(release_id=release_id)
        response = release_client.DeleteRelease(request)
        return {
            "release_id": response.release.release_id,
            "title": response.release.title,
            "date": response.release.date,
            "url": response.release.url,
            "updated_on": response.release.updated_on,
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
        add_request = AddReleaseRequest(release=NewRelease(
            title=str(request_body['title']),
            date=str(request_body['date']),
            url=str(request_body['url']),
            updated_on=int(request_body['updated_on']),
        ))
        response = release_client.AddRelease(add_request)
        return {
            "release_id": response.release.release_id,
            "title": response.release.title,
            "date": response.release.date,
            "url": response.release.url,
            "updated_on": response.release.updated_on,
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

