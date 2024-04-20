FROM python:3.9
RUN mkdir /service

WORKDIR /service/artist_logic
COPY app/artist-logic-service/requirements.txt /service/artist_logic/
RUN pip install -r requirements.txt
COPY app/artist-logic-service/artist_logic.py /service/artist_logic/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 5001
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=artist_logic.py
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0", "--port=5001"]