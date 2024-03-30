FROM python:3.9

RUN mkdir /service

WORKDIR /service/genre_logic
COPY app/genre-logic-service/requirements.txt /service/genre_logic/
RUN pip install -r requirements.txt
COPY app/genre-logic-service/genre_logic.py /service/genre_logic/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 5005
ENV FLASK_APP=genre_logic.py
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0"]
