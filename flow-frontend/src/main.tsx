import React from 'react'
import ReactDOM from 'react-dom/client'
import { Amplify } from 'aws-amplify'
import outputs from './amplify_outputs.json'
import App from './App'
import './index.css'

// Configure Amplify with proper email authentication
const amplifyConfig = {
  aws_project_region: 'us-east-1',
  aws_cognito_region: 'us-east-1',
  aws_user_pools_id: outputs.auth.user_pool_id,
  aws_user_pools_web_client_id: outputs.auth.user_pool_client_id,
  oauth: {},
  aws_cognito_username_attributes: ['email'],
  aws_cognito_social_providers: [],
  aws_cognito_signup_attributes: ['email', 'name'],
  aws_cognito_mfa_configuration: 'OFF',
  aws_cognito_mfa_types: ['SMS'],
  aws_cognito_password_protection_settings: {
    passwordPolicyMinLength: 8,
    passwordPolicyCharacters: [
      'REQUIRES_LOWERCASE',
      'REQUIRES_UPPERCASE', 
      'REQUIRES_NUMBERS'
    ]
  },
  aws_cognito_verification_mechanisms: ['email'],
  aws_cloud_logic_custom: [
    {
      name: 'flow-api',
      endpoint: outputs.custom.API.flow.endpoint,
      region: outputs.custom.API.flow.region
    }
  ]
}

Amplify.configure(amplifyConfig)

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)