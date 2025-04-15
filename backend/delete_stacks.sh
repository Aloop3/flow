#!/bin/bash

# Define the stack names
STACKS=("flow-dev" "flow-layers")

# Delete stacks in the specified order
for STACK in "${STACKS[@]}"; do
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
done

echo "Stack deletion process completed."
