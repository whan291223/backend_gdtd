# Frontend Integration Guide for New Security Updates

The backend now requires authentication and authorization for all user-facing API endpoints. Please update your frontend implementation following these steps:

## 1. Include the Authorization Header

Every request to the user-facing APIs (e.g., `/users/`, `/patient-profile/`, `/food-log/`, etc.) must include a Bearer token in the `Authorization` header.

### How to obtain the token:
Using the LINE LIFF SDK:
```javascript
const idToken = liff.getIDToken();
```

### Example request:
```javascript
const response = await fetch(`https://api.example.com/api/v0.1/patient-profile/${lineUserId}`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${idToken}`,
    'Content-Type': 'application/json'
  }
});
```

## 2. Updated API Logic

- **Identity Verification**: The backend verifies that the `idToken` belongs to the `lineUserId` provided in the path parameter. Ensure you are using the correct `lineUserId` from `liff.getDecodedIDToken().sub` or `liff.getContext().userId`.
- **Ownership Check**: For endpoints like `/test/session/{test_session_id}`, the backend checks if the session record actually belongs to the authenticated user.

## 3. Handle New Error Responses

Your frontend should gracefully handle the following HTTP status codes:

- **401 Unauthorized**:
  - *Cause*: Missing or invalid `Authorization` header, or the token has expired.
  - *Action*: Ensure the user is logged into LIFF and refresh the token if necessary.
- **403 Forbidden**:
  - *Cause*: The authenticated user is trying to access data belonging to another `lineUserId`.
  - *Action*: Alert the user or log them out if this is unexpected.
- **503 Service Unavailable**:
  - *Cause*: The backend was unable to reach LINE's servers to verify the token.
  - *Action*: Retry the request after a short delay.

## 4. Admin API

Note that the Admin API (`/admin/*`) continues to use the `x-admin-token` header and does not require a LINE ID token.
