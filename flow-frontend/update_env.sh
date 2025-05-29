#!/bin/bash

# Updated for 3-stack architecture
ENVIRONMENT=${1:-dev}

if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    echo "Error: Environment must be 'dev' or 'prod'"
    echo "Usage: $0 <environment>"
    echo "Example: $0 dev"
    exit 1
fi

DATA_STACK_NAME="flow-data-${ENVIRONMENT}"
APP_STACK_NAME="flow-app-${ENVIRONMENT}"

echo "Fetching CloudFormation outputs for environment: $ENVIRONMENT"
echo "Data stack: $DATA_STACK_NAME"
echo "App stack: $APP_STACK_NAME"

# Get Cognito info from data stack
echo "Fetching Cognito configuration from data stack..."
DATA_OUTPUTS=$(aws cloudformation describe-stacks --stack-name "$DATA_STACK_NAME" --query "Stacks[0].Outputs" --output json)

if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch data stack outputs. Make sure $DATA_STACK_NAME exists."
    exit 1
fi

USER_POOL_ID=$(echo "$DATA_OUTPUTS" | jq -r '.[] | select(.OutputKey=="UserPoolId") | .OutputValue')
USER_POOL_CLIENT_ID=$(echo "$DATA_OUTPUTS" | jq -r '.[] | select(.OutputKey=="UserPoolClientId") | .OutputValue')

# Get API URL from app stack
echo "Fetching API configuration from app stack..."
APP_OUTPUTS=$(aws cloudformation describe-stacks --stack-name "$APP_STACK_NAME" --query "Stacks[0].Outputs" --output json)

if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch app stack outputs. Make sure $APP_STACK_NAME exists."
    exit 1
fi

RAW_API_URL=$(echo "$APP_OUTPUTS" | jq -r '.[] | select(.OutputKey=="FlowApi") | .OutputValue')
API_URL="${RAW_API_URL%/}"

# Validate we got all required values
if [ "$USER_POOL_ID" = "null" ] || [ -z "$USER_POOL_ID" ]; then
    echo "Error: Could not find UserPoolId in data stack outputs"
    exit 1
fi

if [ "$USER_POOL_CLIENT_ID" = "null" ] || [ -z "$USER_POOL_CLIENT_ID" ]; then
    echo "Error: Could not find UserPoolClientId in data stack outputs"
    exit 1
fi

if [ "$API_URL" = "null" ] || [ -z "$API_URL" ]; then
    echo "Error: Could not find FlowApi in app stack outputs"
    exit 1
fi

# Update .env file
echo "Updating .env file..."
sed -i '' "s|^VITE_USER_POOL_ID=.*|VITE_USER_POOL_ID=${USER_POOL_ID}|" .env
sed -i '' "s|^VITE_USER_POOL_CLIENT_ID=.*|VITE_USER_POOL_CLIENT_ID=${USER_POOL_CLIENT_ID}|" .env
sed -i '' "s|^VITE_API_URL=.*|VITE_API_URL=${API_URL}|" .env

echo "Environment update complete for: $ENVIRONMENT"
echo "  VITE_USER_POOL_ID=${USER_POOL_ID}"
echo "  VITE_USER_POOL_CLIENT_ID=${USER_POOL_CLIENT_ID}"
echo "  VITE_API_URL=${API_URL}"

# Also update main.tsx if it exists
if [ -f "src/main.tsx" ]; then
    echo "Updating src/main.tsx with new endpoint..."
    sed -i '' "s|endpoint: 'https://[^']*'|endpoint: '${API_URL}'|" src/main.tsx
    echo "main.tsx updated successfully"
else
    echo "Note: src/main.tsx not found in current directory"
fi