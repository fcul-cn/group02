FROM python:3.9

RUN mkdir /service

WORKDIR /service/auth-service
COPY app/auth-service/requirements.txt /service/auth-service/
RUN pip install -r requirements.txt
COPY app/auth-service/auth.env /service/auth-service/
COPY app/auth-service/auth-service.py /service/auth-service/
#COPY protobufs/ /service/protobufs/
#RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/app.proto

EXPOSE 5055
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=auth-service.py
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0", "--port=5055" ]
