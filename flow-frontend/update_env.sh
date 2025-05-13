#!/bin/bash

# Replace with your actual stack name
STACK_NAME="flow-dev"

# Fetch CloudFormation outputs
echo "Fetching CloudFormation outputs for stack: $STACK_NAME"
OUTPUTS_JSON=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs" --output json)

# Extract values
USER_POOL_ID=$(echo "$OUTPUTS_JSON" | jq -r '.[] | select(.OutputKey=="UserPoolId") | .OutputValue')
USER_POOL_CLIENT_ID=$(echo "$OUTPUTS_JSON" | jq -r '.[] | select(.OutputKey=="UserPoolClientId") | .OutputValue')
RAW_API_URL=$(echo "$OUTPUTS_JSON" | jq -r '.[] | select(.OutputKey=="FlowApi") | .OutputValue')
API_URL="${RAW_API_URL%/}"

# Update .env file
echo "Updating .env file..."
sed -i '' "s|^VITE_USER_POOL_ID=.*|VITE_USER_POOL_ID=${USER_POOL_ID}|" .env
sed -i '' "s|^VITE_USER_POOL_CLIENT_ID=.*|VITE_USER_POOL_CLIENT_ID=${USER_POOL_CLIENT_ID}|" .env
sed -i '' "s|^VITE_API_URL=.*|VITE_API_URL=${API_URL}|" .env

echo "Update complete:"
echo "  VITE_USER_POOL_ID=${USER_POOL_ID}"
echo "  VITE_USER_POOL_CLIENT_ID=${USER_POOL_CLIENT_ID}"
echo "  VITE_API_URL=${API_URL}"
