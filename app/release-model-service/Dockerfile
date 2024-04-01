FROM python:3.9

RUN mkdir /service

WORKDIR /service/track_model
COPY app/track-model-service/requirements.txt /service/track_model/
RUN pip install -r requirements.txt
COPY app/track-model-service/track_model.py /service/track_model/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 50051
CMD  [ "python", "-u", "track_model.py" ]