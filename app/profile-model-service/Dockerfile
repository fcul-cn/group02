FROM python:3.9

RUN mkdir /service

WORKDIR /service/profile_model
COPY app/profile-model-service/requirements.txt /service/profile_model/
RUN pip install -r requirements.txt
COPY app/profile-model-service/profile_model.py /service/profile_model/
COPY protobufs/ /service/protobufs/
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/profile.proto

EXPOSE 50051
CMD  [ "python", "-u", "profile_model.py" ]