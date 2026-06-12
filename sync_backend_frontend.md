# API Synchronization Documentation

This document summarizes the synchronization between the backend (FastAPI) and the frontend TypeScript definitions for the Admin API.

## Patient Detail and History

The `PatientDetail` structure in `api/admin_api.py` (via the `_get_patient_detail` helper) is fully synced with the frontend requirement. It includes:
-   **Identity & Profile:** `userId`, `lineUserId`, `displayName`, `pictureUrl`, `firstName`, `lastName`, `age`, `gender`, `phone`, `height`, `weight`, `bmi`, `bloodPressure`, `existingDiseases`, `smoking`, `alcohol`, `urineAmount`.
-   **Today's Setup:** `dailySetup` (current UTC date).
-   **Full Histories:**
    -   `spentNafHistory` (all sessions).
    -   `bloodTestHistory` (all records).
    -   `foodLogHistory` (limit 200).
    -   `exerciseLogHistory` (limit 100).
    -   `dailySetupHistory` (limit 100).
    -   `labHistory` (all custom lab records).
-   **Calculated Targets:** `nutritionTargets` based on current weight and urine amount.
-   **Configuration:** `labConfig`.

## Offline Patient Creation

The `POST /admin/patients` endpoint now supports creating patients without a `lineUserId`.

-   **Backend Logic:** If `lineUserId` is omitted in the request body, the server automatically generates a unique placeholder ID in the format `OFFLINE_{uuid}` (e.g., `OFFLINE_a1b2c3d4e5f6`).
-   **Frontend Change:** No changes are required to the `AdminPatientRegistrationPage`. It can safely send the payload without a `lineUserId` field.

## New Admin Endpoints

The following endpoints have been added/updated to match frontend `adminApi.ts` signatures:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/admin/patients` | Create a new patient (and user if needed). |
| `POST` | `/admin/patients/{user_id}/spent` | Submit SPENT screening for a user. |
| `PUT` | `/admin/test/naf/{test_session_id}` | Submit NAF assessment for a session. |
| `PUT` | `/admin/patients/{user_id}` | Update patient profile and refresh detail. |

## Serialization

All API responses use `camelCase` for JSON keys (handled via `alias_generator` in `schema/config.py`), matching the frontend expectations.
