FROM python:3.9

RUN mkdir /service

WORKDIR /service/track_logic
COPY app/track-logic-service/requirements.txt /service/track_logic/
RUN pip install -r requirements.txt
COPY app/track-logic-service/track_logic.py /service/track_logic/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 5000
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=track_logic.py
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0"]
