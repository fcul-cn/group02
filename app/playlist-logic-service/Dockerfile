FROM python:3.9

RUN mkdir /service

WORKDIR /service/playlist_logic
COPY app/playlist-logic-service/requirements.txt /service/playlist_logic/
RUN pip install -r requirements.txt
COPY app/playlist-logic-service/playlist_logic.py /service/playlist_logic/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 5003
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=playlist_logic.py
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0", "--port=5003"]
