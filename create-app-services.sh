#!/bin/bash

set -euo pipefail

# --- Configuration and defaults ---
RESOURCE_GROUP="${1:-gaurav_psmarket}"
APP_SERVICE_PLAN="${2:-psmarket-linux-plan}"
LOCATION="${3:-EastUS}"
ACR_NAME="${4:-gauravacr}"
APP_SERVICE_PLAN_SKU="B1"
RUNTIME="DOTNETCORE|6.0"
LOG_FILE="deployment.log"
MAX_RETRIES=3
RETRY_DELAY=5  # seconds
DRY_RUN=false
TAGS="Environment=Dev Owner=Gaurav Project=PSMarket"

# --- Functions ---
log() {
  local msg="$1"
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $msg" | tee -a "$LOG_FILE"
}

retry_command() {
  local n=0
  local cmd="$*"
  until [ $n -ge $MAX_RETRIES ]
  do
    $cmd && return 0
    n=$((n+1))
    log "Command failed: $cmd. Retry $n/$MAX_RETRIES in $RETRY_DELAY seconds."
    sleep $RETRY_DELAY
  done
  log "Command failed after $MAX_RETRIES attempts: $cmd"
  exit 1
}

print_usage() {
  echo "Usage: $0 [--dry-run] [RESOURCE_GROUP] [APP_SERVICE_PLAN] [LOCATION] [ACR_NAME]"
  echo "Example: $0 --dry-run mygroup myplan eastus acrname"
}

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

# --- Validation ---
if ! command -v az &> /dev/null; then
  echo "Azure CLI not found. Please install and login."
  exit 1
fi

if ! az account show &> /dev/null; then
  echo "Azure CLI not logged in. Please run 'az login'."
  exit 1
fi

log "Starting deployment script. Dry run mode = $DRY_RUN"

if [ "$DRY_RUN" = true ]; then
  log "Dry run enabled. No resources will be created or modified."
fi

run_or_dry() {
  if [ "$DRY_RUN" = true ]; then
    log "[Dry run] $*"
  else
    retry_command "$@"
  fi
}

# --- Environment-specific overrides ---
if [[ "$RESOURCE_GROUP" == *prod* ]]; then
  APP_SERVICE_PLAN_SKU="S2"
  MAX_RETRIES=5
  RETRY_DELAY=10
  TAGS="Environment=Production Owner=Gaurav Project=PSMarket"
  log "Production environment detected: applying prod configurations."
fi

start_time=$(date +%s)

# --- Resource Group Creation ---
if az group exists --name "$RESOURCE_GROUP"; then
  log "Resource group $RESOURCE_GROUP exists."
else
  log "Creating resource group $RESOURCE_GROUP with tags: $TAGS"
  run_or_dry az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --tags $TAGS
fi

# --- App Service Plan Creation ---
if az appservice plan show --name "$APP_SERVICE_PLAN" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
  log "App Service plan $APP_SERVICE_PLAN exists."
else
  log "Creating App Service plan $APP_SERVICE_PLAN with SKU $APP_SERVICE_PLAN_SKU and tags: $TAGS"
  run_or_dry az appservice plan create --name "$APP_SERVICE_PLAN" --resource-group "$RESOURCE_GROUP" --sku "$APP_SERVICE_PLAN_SKU" --is-linux --location "$LOCATION" --tags $TAGS
fi

# --- Services and their ports ---
declare -A services_ports=(
  [auth_service]=8009
  [product_catalog]=8001
  [inventory]=8002
  [order]=8003
  [payment]=8004
  [billing]=8005
  [delivery]=8006
  [notification]=8007
  [notification_bridge]=""
  [store_onboarding]=8008
  [api_gateway]=8080
)

# --- Create/Update Web Apps ---
for service in "${!services_ports[@]}"; do
  app_name="$service-app"
  port=${services_ports[$service]}

  if az webapp show --name "$app_name" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
    log "App Service $app_name exists. Updating container image."
    run_or_dry az webapp config container set --name "$app_name" --resource-group "$RESOURCE_GROUP" --docker-custom-image-name "$ACR_NAME.azurecr.io/$service:latest"
  else
    log "App Service $app_name does not exist. Creating with tags: $TAGS"
    run_or_dry az webapp create --name "$app_name" --resource-group "$RESOURCE_GROUP" --plan "$APP_SERVICE_PLAN" --runtime "$RUNTIME" --deployment-container-image-name "$ACR_NAME.azurecr.io/$service:latest" --tags $TAGS
  fi

  if [ -n "$port" ]; then
    log "Setting WEBSITES_PORT=$port and health check path for $app_name."
    run_or_dry az webapp config appsettings set --name "$app_name" --resource-group "$RESOURCE_GROUP" --settings WEBSITES_PORT="$port"
    run_or_dry az webapp config set --name "$app_name" --resource-group "$RESOURCE_GROUP" \
      --generic-configurations '{"healthCheckPath": "/health"}'
  else
    log "No port defined for $app_name, skipping WEBSITES_PORT and health check."
  fi
done

duration=$(( $(date +%s) - start_time ))
log "Deployment completed in $duration seconds."

# Exit success
exit 0
