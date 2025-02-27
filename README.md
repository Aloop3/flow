# Flow

**Flow** is a mobile-friendly web app designed to streamline workout tracking for powerlifting and training program management for athletes and coaches. It leverages modern web technologies and AWS services to provide an efficient, scalable, and seamless experience for users.

## Features

### User Types

- **Athlete**: View personalized workout programs, log exercises, and track progress within training blocks.
- **Coach**: Create and manage workout programs for athletes, with the ability to track progress and adjust training plans.

### Workout Blocks

- A **Block** is a program created by a Coach for an Athlete (or by an Athlete for themselves).
- Each **Block** contains multiple **Weeks**, and each **Week** contains **Days**.
- Each **Day** consists of multiple **Exercises** that athletes need to perform.

### Analytics

- Aggregate exercise data to provide insights, such as 1RM history, training volume, and performance trends.

### AWS Integration

- **DynamoDB**: For data storage, ensuring scalable, fast access to workout data.
- **AWS Lambda**: For serverless backend operations, reducing the need for managing servers.
- **Amazon Cognito**: Used for role-based authentication, enabling secure login and access control for athletes and coaches.
- **AWS SAM (Serverless Application Model)**: Used for deploying the app and managing serverless resources.
- **AWS CodePipeline**: Ensures smooth CI/CD workflows for deploying updates and maintaining a reliable production environment.

## Usage (Planned)

### For Athletes

1. Sign up for an account.
2. Connect with your coach (if applicable).
3. View your assigned training blocks.
4. Log your workouts and track progress.

### For Coaches

1. Create an account.
2. Add athletes to your roster.
3. Create and assign training blocks.
4. Monitor athlete progress and make adjustments as needed.

## Architecture

Flow uses a serverless architecture with AWS services:

- **Frontend**: React.js with responsive design for mobile compatibility.
- **Backend**: AWS Lambda functions.
- **Database**: DynamoDB.
- **Authentication**: Amazon Cognito.
- **Deployment**: AWS SAM and CodePipeline.