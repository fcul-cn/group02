from concurrent import futures
import grpc
from grpc_interceptor import ExceptionToStatusInterceptor
from track_pb2 import (
    GetTrackResponse,
    DeleteTrackResponse,
    AddTrackResponse,
    GetTrackGenreResponse
)
import track_pb2_grpc

# TODO
class TrackService(track_pb2_grpc.TrackServiceServicer):
    def getTrack(self, request, context):
        return GetTrackResponse() 

    def deleteTrack(self, request, context):
        return DeleteTrackResponse()

    def addTrack(self, request, context):
        return AddTrackResponse()

    def getTrackGenre(self, request, context):
        return GetTrackGenreResponse()


def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    track_pb2_grpc.add_RecommendationsServicer_to_server(
        TrackService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
