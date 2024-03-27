from concurrent import futures
import grpc
from grpc_interceptor import ExceptionToStatusInterceptor
from artist_pb2 import (
    GetArtistResponse,
    AddArtistResponse,
    GetArtistReleasesResponse,
)
import artist_pb2_grpc

# TODO
class ArtistService(artist_pb2_grpc.ArtistService):
    def getArtist(self, request, context):
        return GetArtistResponse() 
    def addArtist(self, request, context):
        return AddArtistResponse() 
    def getArtistReleases(self, request, context):
        return GetArtistReleasesResponse() 



def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    artist_pb2_grpc.add_RecommendationsServicer_to_server(
        ArtistService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
