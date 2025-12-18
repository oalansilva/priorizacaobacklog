# Change Proposal: Use Lambda Function URL

## Context
The application currently relies on relative paths or potentially old API Gateway URLs. The user wants to strictly enforce the use of the new Lambda Function URL: `https://4tgupu7jynssz7q4ivevmdmsau0hyxjd.lambda-url.us-east-1.on.aws/`.

## Proposed Changes
1.  **Frontend**: Configure `axios` in `App.jsx` to use the Lambda Function URL as the `baseURL` by default.
2.  **Scripts**: Update `scripts/deploy_dev.ps1` to display the correct URL upon successful deployment.

## Justification
Ensures consistency and prevents connection errors or connecting to the wrong backend, especially during local development.
