import React from 'react'
import ReactDOM from 'react-dom/client'
import { Amplify } from 'aws-amplify'
import App from './App'
import './index.css'


const amplifyConfig = {
 aws_project_region: 'us-east-1',
 aws_cognito_region: 'us-east-1',
 aws_user_pools_id: import.meta.env.VITE_USER_POOL_ID || '',
 aws_user_pools_web_client_id: import.meta.env.VITE_USER_POOL_CLIENT_ID || '',
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
     endpoint: import.meta.env.VITE_API_URL || '',
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
