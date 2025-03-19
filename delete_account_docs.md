# Account Deletion Feature - Frontend Integration Guide

## Overview

We've implemented a new feature to delete Instagram accounts from tracking across both the Logic Service and Scraper Service. This document provides integration details for the frontend team.

## Primary Endpoint (Recommended)

### Delete Account and All Associated Data

```
DELETE /api/v1/accounts/{username}
```

#### Path Parameters
- `username` (string, required): The Instagram username to delete from tracking

#### Response

- **Success (200 OK)**
  ```json
  {
    "status": "success",
    "message": "Account 'username' and all associated profile data deleted successfully",
    "account": {
      "id": 123,
      "username": "instagram",
      "status": "active",
      "created_at": "2023-01-01T00:00:00"
    }
  }
  ```

- **Not Found (404)**
  ```json
  {
    "detail": "Account 'username' not found in database"
  }
  ```
  or
  ```json
  {
    "detail": "Failed to delete username from scraper service"
  }
  ```

## Alternative Direct Endpoint (Advanced Use Only)

If you need to directly delete an account only from the scraper service (not recommended for normal use):

```
DELETE /api/v1/scraper/delete-account/{username}
```

#### Path Parameters
- `username` (string, required): The Instagram username to delete

#### Response
Same format as the scraper service response.

## Important Notes

1. Account deletion is **permanent** - all historical profile data will be lost
2. There is no confirmation step - deletion happens immediately 
3. The operation cannot be undone
4. The endpoint automatically clears all related cache entries

## Integration Example

```javascript
async function deleteAccount(username) {
  try {
    const response = await fetch(`/api/v1/accounts/${username}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete account');
    }
    
    const data = await response.json();
    console.log(data.message);
    return data;
  } catch (error) {
    console.error('Error deleting account:', error);
    throw error;
  }
}
```

## Implementation Details

The deletion process follows these steps:
1. Deletes the account from the Scraper Service 
2. Deletes the account from the Logic Service database (cascades to profile data)
3. Clears all cached data related to the account

## UI Recommendations

We recommend implementing:
- A confirmation dialog with clear warnings about permanent deletion
- Visual feedback during the deletion process
- Clear error messaging if deletion fails