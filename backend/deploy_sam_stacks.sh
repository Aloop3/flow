#!/bin/bash

# Flow SAM Deployment Script - 3-Stack Architecture
set -e

ENVIRONMENT=${1:-dev}
CORS_ORIGIN=${2:-'https://dev.dykl7ea8q4fpo.amplifyapp.com'}
LAYER_VERSION=${3:-v0-1-0}

echo "Deploying to environment: $ENVIRONMENT"
echo "CORS Origin: $CORS_ORIGIN"
echo "Layer Version: $LAYER_VERSION"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    echo "Error: Environment must be 'dev' or 'prod'"
    echo "Usage: $0 <environment> [cors-origin] [layer-version]"
    echo "Example: $0 dev"
    echo "Example: $0 prod 'https://app.myflow.com' v1-0-0"
    exit 1
fi

# Define template files
LAYER_TEMPLATE="layers.yaml"
DATA_TEMPLATE="data-stack.yaml"
APP_TEMPLATE="app-stack.yaml"

# Step 1: Deploy Layers (if needed)
echo "Step 1: Validating and deploying layers..."
sam validate --lint -t "$LAYER_TEMPLATE"

if [ $? -ne 0 ]; then
  echo "SAM layers template validation failed."
  exit 1
else
  echo "SAM layers template validated successfully."
fi

sam build -t "$LAYER_TEMPLATE"
sam deploy -t "$LAYER_TEMPLATE" \
    --stack-name flow-layers \
    --parameter-overrides LayerVersion=${LAYER_VERSION}

if [ $? -ne 0 ]; then
  echo "Failed to deploy layers stack."
  exit 1
fi

# Step 2: Deploy Data Stack
echo "Step 2: Validating and deploying data stack..."
sam validate --lint -t "$DATA_TEMPLATE"

if [ $? -ne 0 ]; then
  echo "Data stack template validation failed."
  exit 1
else
  echo "Data stack template validated successfully."
fi

sam build -t "$DATA_TEMPLATE"
sam deploy -t "$DATA_TEMPLATE" \
    --stack-name "flow-data-${ENVIRONMENT}" \
    --parameter-overrides Environment=${ENVIRONMENT} LayerVersion=${LAYER_VERSION}

if [ $? -ne 0 ]; then
  echo "Failed to deploy data stack."
  exit 1
fi

# Step 3: Deploy App Stack  
echo "Step 3: Validating and deploying app stack..."
sam validate --lint -t "$APP_TEMPLATE"

if [ $? -ne 0 ]; then
  echo "App stack template validation failed."
  exit 1
else
  echo "App stack template validated successfully."
fi

sam build -t "$APP_TEMPLATE"
sam deploy -t "$APP_TEMPLATE" \
    --stack-name "flow-app-${ENVIRONMENT}" \
    --parameter-overrides Environment=${ENVIRONMENT} CorsOrigin="${CORS_ORIGIN}" LayerVersion=${LAYER_VERSION}

if [ $? -ne 0 ]; then
  echo "Failed to deploy app stack."
  exit 1
fi

echo "✅ Deployment complete for environment: $ENVIRONMENT"
echo ""
echo "Stack Names:"
echo "- Layers: flow-layers (version: ${LAYER_VERSION})"
echo "- Data: flow-data-${ENVIRONMENT}"
echo "- App: flow-app-${ENVIRONMENT}"
echo ""
echo "To get API URL:"
echo "aws cloudformation describe-stacks --stack-name flow-app-${ENVIRONMENT} --query 'Stacks[0].Outputs[?OutputKey==\`FlowApi\`].OutputValue' --output text"