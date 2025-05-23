import { defineBackend } from '@aws-amplify/backend';
import * as dotenv from 'dotenv';

dotenv.config();

const backend = defineBackend({
});

backend.addOutput({
  auth: {
    aws_region: 'us-east-1',
    user_pool_id: process.env.VITE_USER_POOL_ID || '',
    user_pool_client_id: process.env.VITE_USER_POOL_CLIENT_ID || '',
    identity_pool_id: undefined,
    password_policy: {
      min_length: 8,
      require_lowercase: true,
      require_uppercase: true,
      require_numbers: true,
      require_symbols: false,
    },
  },
  custom: {
    API: {
      flow: {
        endpoint: process.env.VITE_API_URL || '',
        region: 'us-east-1',
      }
    }
  }
});