#!/bin/bash

#Cluster
gcloud container clusters create hello-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-8 \
  --zone=europe-west4-a

#Secrets
kubectl create secret generic json-key --from-literal "API_TOKEN=$(cat JSON-KEY.json)"
kubectl create secret docker-registry artifact-registry --docker-server=https://europe-west4-docker.pkg.dev/ --docker-email=artifact-project-cn@confident-facet-329316.iam.gserviceaccount.com --docker-username=_json_key --docker-password="$(cat ARTIFACT-REGISTRY.json)"

#Deployment
kubectl apply -f deployment.yaml






