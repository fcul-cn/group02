FROM python:3.9

RUN mkdir /service

WORKDIR /service/playlist_model
COPY app/playlist-model-service/requirements.txt /service/playlist_model/
RUN pip install -r requirements.txt
COPY app/playlist-model-service/playlist_model.py /service/playlist_model/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 50057
CMD  [ "python", "-u", "playlist_model.py" ]