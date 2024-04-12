FROM python:3.9
RUN mkdir /service

WORKDIR /service/artistsReleases_model
COPY app/artistsReleases-model-service/requirements.txt /service/artistsReleases_model/
RUN pip install -r requirements.txt
COPY app/artistsReleases-model-service/artistsReleases_model.py /service/artistsReleases_model/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 50053
CMD  [ "python", "-u", "artistsReleases_model.py" ]