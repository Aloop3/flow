#!/bin/bash

# Flow Environment-Isolated Architecture Deletion Script
# Delete in reverse order (app -> data -> layers)
set -e

ENVIRONMENT=${1:-dev}

if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    echo "Error: Environment must be 'dev' or 'prod'"
    echo "Usage: $0 <environment>"
    echo "Example: $0 dev"
    echo "Example: $0 prod"
    exit 1
fi

STACKS=(
  "flow-app-${ENVIRONMENT}"
  "flow-data-${ENVIRONMENT}" 
  "flow-layers-${ENVIRONMENT}"
)

echo "Deleting Flow stacks for environment: $ENVIRONMENT"
echo "Stacks to delete: ${STACKS[@]}"

# Delete stacks in the specified order
for STACK in "${STACKS[@]}"; do
  echo "Checking if stack $STACK exists..."
  
  # Check if stack exists before trying to delete
  if aws cloudformation describe-stacks --stack-name "$STACK" >/dev/null 2>&1; then
    echo "Deleting stack: $STACK"
    aws cloudformation delete-stack --stack-name "$STACK"
    
    # Wait until the stack deletion is complete
    echo "Waiting for stack $STACK to be deleted..."
    aws cloudformation wait stack-delete-complete --stack-name "$STACK"
    
    if [ $? -eq 0 ]; then
      echo "Stack $STACK deleted successfully."
    else
      echo "Failed to delete stack $STACK."
    fi
  else
    echo "Stack $STACK does not exist, skipping..."
  fi
done

echo "Stack deletion process completed for environment: $ENVIRONMENT"
echo ""
echo "ℹ️  Note: This deletes only ${ENVIRONMENT} environment."
echo "   Other environments (dev/prod) remain unaffected."