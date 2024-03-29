FROM python:3.9

RUN mkdir /service

WORKDIR /service/genre_model
COPY app/genre-model-service/requirements.txt /service/genre_model/
RUN pip install -r requirements.txt
COPY app/genre-model-service/genre_model.py /service/genre_model/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/genre.proto

EXPOSE 50055
CMD  [ "python", "-u", "genre_model.py" ]