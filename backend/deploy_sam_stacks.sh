#!/bin/bash

# Flow SAM Deployment Script - Environment-Isolated Architecture
set -e

ENVIRONMENT=${1:-dev}
CORS_ORIGIN=${2:-'https://dev.dykl7ea8q4fpo.amplifyapp.com'}
LAYER_VERSION=${3:-v0-1-0}
ALERT_EMAIL=${4:-''}

echo "🚀 Deploying Flow to environment: $ENVIRONMENT"
echo "📍 CORS Origin: $CORS_ORIGIN"
echo "🏷️  Layer Version: $LAYER_VERSION"
echo "📧 Alert Email: $ALERT_EMAIL"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    echo "❌ Error: Environment must be 'dev' or 'prod'"
    echo "Usage: $0 <environment> [cors-origin] [layer-version] [alert-email]"
    echo "Example: $0 dev"
    echo "Example: $0 prod 'https://prod.d3n7bxbkj4ddz8.amplifyapp.com' v0-1-0 'your@email.com'"
    exit 1
fi

# Validate alert email for prod environment
if [[ "$ENVIRONMENT" == "prod" ]] && [[ -z "$ALERT_EMAIL" ]]; then
    echo "❌ Error: Alert email is required for production environment"
    echo "Usage: $0 prod <cors-origin> <layer-version> <alert-email>"
    echo "Example: $0 prod 'https://prod.d3n7bxbkj4ddz8.amplifyapp.com' v0-1-0 'your@email.com'"
    exit 1
fi

# Define template files
LAYER_TEMPLATE="layers.yaml"
DATA_TEMPLATE="data-stack.yaml"
APP_TEMPLATE="app-stack.yaml"

# Common SAM deploy flags to prevent hanging
SAM_DEPLOY_FLAGS="--no-confirm-changeset --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM"

# Step 1: Deploy Environment-Specific Layers
echo "📦 Step 1: Validating and deploying layers for ${ENVIRONMENT}..."
sam validate --lint -t "$LAYER_TEMPLATE"

if [ $? -ne 0 ]; then
  echo "❌ SAM layers template validation failed."
  exit 1
else
  echo "✅ SAM layers template validated successfully."
fi

sam build -t "$LAYER_TEMPLATE"
sam deploy -t "$LAYER_TEMPLATE" \
    --stack-name "flow-layers-${ENVIRONMENT}" \
    --parameter-overrides LayerVersion=${LAYER_VERSION} Environment=${ENVIRONMENT} \
    $SAM_DEPLOY_FLAGS

if [ $? -ne 0 ]; then
  echo "❌ Failed to deploy layers stack."
  exit 1
else
  echo "✅ Layers stack deployed successfully."
fi

# Step 2: Deploy Data Stack
echo "🗄️  Step 2: Validating and deploying data stack..."
sam validate --lint -t "$DATA_TEMPLATE"

if [ $? -ne 0 ]; then
  echo "❌ Data stack template validation failed."
  exit 1
else
  echo "✅ Data stack template validated successfully."
fi

sam build -t "$DATA_TEMPLATE"
sam deploy -t "$DATA_TEMPLATE" \
    --stack-name "flow-data-${ENVIRONMENT}" \
    --parameter-overrides Environment=${ENVIRONMENT} LayerVersion=${LAYER_VERSION} \
    $SAM_DEPLOY_FLAGS

if [ $? -ne 0 ]; then
  echo "❌ Failed to deploy data stack."
  exit 1
else
  echo "✅ Data stack deployed successfully."
fi

# Step 3: Deploy App Stack  
echo "⚡ Step 3: Validating and deploying app stack..."
sam validate --lint -t "$APP_TEMPLATE"

if [ $? -ne 0 ]; then
  echo "❌ App stack template validation failed."
  exit 1
else
  echo "✅ App stack template validated successfully."
fi

sam build -t "$APP_TEMPLATE"
sam deploy -t "$APP_TEMPLATE" \
    --stack-name "flow-app-${ENVIRONMENT}" \
    --parameter-overrides Environment=${ENVIRONMENT} CorsOrigin="${CORS_ORIGIN}" LayerVersion=${LAYER_VERSION} AlertEmail="${ALERT_EMAIL}" \
    $SAM_DEPLOY_FLAGS

if [ $? -ne 0 ]; then
  echo "❌ Failed to deploy app stack."
  exit 1
else
  echo "✅ App stack deployed successfully."
fi

# Get API URL for validation
echo "🔍 Fetching API URL..."
API_URL=$(aws cloudformation describe-stacks --stack-name "flow-app-${ENVIRONMENT}" --query 'Stacks[0].Outputs[?OutputKey==`FlowApi`].OutputValue' --output text 2>/dev/null || echo "")

if [ -n "$API_URL" ]; then
    echo "✅ API URL: $API_URL"
else
    echo "⚠️  Warning: Could not retrieve API URL"
fi

echo ""
echo "🎉 Deployment complete for environment: $ENVIRONMENT"
echo ""
echo "📋 Stack Names:"
echo "- Layers: flow-layers-${ENVIRONMENT} (version: ${LAYER_VERSION})"
echo "- Data: flow-data-${ENVIRONMENT}"
echo "- App: flow-app-${ENVIRONMENT}"
echo ""
if [ -n "$API_URL" ]; then
    echo "🌐 API URL: $API_URL"
fi