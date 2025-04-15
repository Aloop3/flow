#!/bin/bash

# Define the SAM template files
LAYER_TEMPLATE="layers.yaml"
MAIN_TEMPLATE="template.yaml"

# Validate the SAM layers template
echo "Validating SAM layers template $LAYER_TEMPLATE"
sam validate --lint -t "$LAYER_TEMPLATE"

if [ $? -ne 0 ]; then
  echo "SAM layers template validation failed."
  exit 1
else
  echo "SAM layers template validated successfully."
fi

# Validate the main SAM template
echo "Validating main SAM template $MAIN_TEMPLATE"
sam validate --lint -t "$MAIN_TEMPLATE"

if [ $? -ne 0 ]; then
  echo "Main SAM template validation failed."
  exit 1
else
  echo "Main SAM template validated successfully."
fi

# Build and deploy the SAM layers
echo "Building SAM layers using $LAYER_TEMPLATE"
sam build -t "$LAYER_TEMPLATE"

echo "Deploying SAM layers"
sam deploy -t "$LAYER_TEMPLATE" --stack-name flow-layers

if [ $? -eq 0 ]; then
  echo "SAM layers deployed successfully."
else
  echo "Failed to deploy SAM layers."
  exit 1
fi

# Build and deploy the main SAM template
echo "Building main SAM application using $MAIN_TEMPLATE"
sam build -t "$MAIN_TEMPLATE"

echo "Deploying main SAM application"
sam deploy -t "$MAIN_TEMPLATE"

if [ $? -eq 0 ]; then
  echo "SAM application deployed successfully."
else
  echo "Failed to deploy SAM application."
  exit 1
fi

echo "SAM build and deploy process completed."