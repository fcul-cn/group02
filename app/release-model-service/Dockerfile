FROM python:3.9

RUN mkdir /service

WORKDIR /service/release_model
COPY app/release-model-service/requirements.txt /service/release_model/
RUN pip install -r requirements.txt
COPY app/release-model-service/release_model.py /service/release_model/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 50058
CMD  [ "python", "-u", "release_model.py" ]