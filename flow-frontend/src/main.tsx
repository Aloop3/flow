import React from 'react'
import ReactDOM from 'react-dom/client'
import { Amplify } from 'aws-amplify'
import App from './App'
import './index.css'

const amplifyConfig = {
  aws_project_region: 'us-east-1',
  aws_cognito_region: 'us-east-1',
  aws_user_pools_id: 'us-east-1_QqzemDqRL',
  aws_user_pools_web_client_id: '18q46vrf08gujmp7q6t3j8h28l',
  oauth: {},
  aws_cognito_social_providers: [],
  aws_cognito_signup_attributes: ['email', 'name'],
  aws_cognito_mfa_configuration: 'OFF',
  aws_cognito_mfa_types: ['EMAIL'],
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
      endpoint: 'https://hwrsjo20w9.execute-api.us-east-1.amazonaws.com/dev',
      region: 'us-east-1'
    }
  ]
}

Amplify.configure(amplifyConfig)

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)