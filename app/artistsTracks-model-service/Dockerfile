FROM python:3.9
RUN mkdir /service

WORKDIR /service/artistsTracks_model
COPY app/artistsTracks-model-service/requirements.txt /service/artistsTracks_model/
RUN pip install -r requirements.txt
# Download grpc_health_probe
RUN wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.4.4/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe
COPY app/artistsTracks-model-service/artistsTracks_model.py /service/artistsTracks_model/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 50054
CMD  [ "python", "-u", "artistsTracks_model.py" ]