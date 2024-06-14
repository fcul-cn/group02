#!/bin/bash

#Cluster
gcloud container clusters create hello-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-4 \
  --zone=europe-west4-a \
  --disk-type pd-standard

#Docker and Artifact Registry Secrets
kubectl create secret generic json-key --from-literal "API_TOKEN=$(cat JSON-KEY.json)" 
kubectl create secret docker-registry artifact-registry --docker-server=https://europe-west4-docker.pkg.dev/ --docker-email=artifact-registry@fcul-cn-ads.iam.gserviceaccount.com --docker-username=_json_key --docker-password="$(cat ARTIFACT-REGISTRY.json)"

#Istio
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.22.0 TARGET_ARCH=x86_64 sh -
export PATH="$PATH:/home/$USER/group02/istio-1.21.2/bin"
yes | istioctl install
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=*"
kubectl create -n istio-system secret tls istio-ingressgateway-certs --key tls.key --cert tls.crt
kubectl create secret generic grafana-admin-credentials --from-env-file=grafana-admin-credentials.env -n istio-system
kubectl create secret generic app-credentials --from-env-file=app-credentials.env
kubectl label namespace default istio-injection=enabled prometheus-monitoring=enabled

#Deploy
kubectl apply -f manifests








