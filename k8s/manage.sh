#!/bin/bash
set -e

ACTION=$1

if [[ "$ACTION" == "apply" ]]; then
  echo "Applying infra manifests..."
  kubectl apply -f k8s/infra/
  echo "Applying service manifests..."
  kubectl apply -f k8s/services/
  echo "All manifests applied."
elif [[ "$ACTION" == "delete" ]]; then
  echo "Deleting service manifests..."
  kubectl delete -f k8s/services/ --ignore-not-found
  echo "Deleting infra manifests..."
  kubectl delete -f k8s/infra/ --ignore-not-found
  echo "All manifests deleted."
else
  echo "Usage: $0 [apply|delete]"
  exit 1
fi
