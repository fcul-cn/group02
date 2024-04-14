FROM python:3.9

RUN mkdir /service

WORKDIR /service/release_model
COPY app/release-model-service/requirements.txt /service/release_model/
RUN pip install -r requirements.txt
# Download grpc_health_probe
RUN wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.4.4/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe
COPY app/release-model-service/release_model.py /service/release_model/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 50058
CMD  [ "python", "-u", "release_model.py" ]