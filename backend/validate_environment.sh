#!/bin/bash

# Flow Environment Validation Script
set -e

ENVIRONMENT=${1:-dev}

if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    echo "Error: Environment must be 'dev' or 'prod'"
    exit 1
fi

echo "🔍 Validating Flow environment: $ENVIRONMENT"
echo "================================================"

# Stack validation
STACKS=("flow-layers" "flow-data-${ENVIRONMENT}" "flow-app-${ENVIRONMENT}")
echo "✅ Checking CloudFormation stacks..."

for STACK in "${STACKS[@]}"; do
    STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK" --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$STATUS" = "CREATE_COMPLETE" ] || [ "$STATUS" = "UPDATE_COMPLETE" ]; then
        echo "  ✅ $STACK: $STATUS"
    else
        echo "  ❌ $STACK: $STATUS"
        exit 1
    fi
done

# API Gateway validation
echo "✅ Checking API Gateway endpoint..."
API_URL=$(aws cloudformation describe-stacks --stack-name "flow-app-${ENVIRONMENT}" --query "Stacks[0].Outputs[?OutputKey=='FlowApi'].OutputValue" --output text)

if [ -n "$API_URL" ]; then
    echo "  ✅ API URL: $API_URL"
    
    # Test API health (if you have a healthy endpoint)
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}users" -H "Authorization: Bearer fake-token" || echo "000")
    if [ "$HTTP_STATUS" = "401" ]; then
        echo "  ✅ API responding (401 expected without auth)"
    else
        echo "  ⚠️  API response: $HTTP_STATUS"
    fi
else
    echo "  ❌ API URL not found"
    exit 1
fi

# Cognito validation
echo "✅ Checking Cognito configuration..."
USER_POOL_ID=$(aws cloudformation describe-stacks --stack-name "flow-data-${ENVIRONMENT}" --query "Stacks[0].Outputs[?OutputKey=='UserPoolId'].OutputValue" --output text)
USER_POOL_CLIENT_ID=$(aws cloudformation describe-stacks --stack-name "flow-data-${ENVIRONMENT}" --query "Stacks[0].Outputs[?OutputKey=='UserPoolClientId'].OutputValue" --output text)

if [ -n "$USER_POOL_ID" ] && [ -n "$USER_POOL_CLIENT_ID" ]; then
    echo "  ✅ User Pool ID: $USER_POOL_ID"
    echo "  ✅ Client ID: $USER_POOL_CLIENT_ID"
else
    echo "  ❌ Cognito configuration incomplete"
    exit 1
fi

# DynamoDB tables validation
echo "✅ Checking DynamoDB tables..."
EXPECTED_TABLES=("users" "blocks" "weeks" "days" "exercises" "workouts" "relationships")

for TABLE in "${EXPECTED_TABLES[@]}"; do
    TABLE_NAME="flow-${ENVIRONMENT}-${TABLE}"
    STATUS=$(aws dynamodb describe-table --table-name "$TABLE_NAME" --query 'Table.TableStatus' --output text 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$STATUS" = "ACTIVE" ]; then
        echo "  ✅ $TABLE_NAME: ACTIVE"
    else
        echo "  ❌ $TABLE_NAME: $STATUS"
        exit 1
    fi
done

echo ""
echo "🎉 Environment validation complete for: $ENVIRONMENT"
echo "All systems operational!"