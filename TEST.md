# Testing Guide for Konnect + Supabase

This document provides instructions on how to test the features implemented during the migration to Supabase.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- Node.js and npm
- Supabase CLI

## 1. Environment Setup

1.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    npm install
    ```

2.  **Configure Environment Variables:**

    Your `.env` file should be configured with your Supabase project credentials. It should look like this:

    ```
    DATABASE_URL=postgresql://postgres:<your-db-password>@db.<project-ref>.supabase.co:5432/postgres
    REDIS_URL=redis://localhost:6379/0
    CELERY_BROKER_URL=redis://localhost:6379/1
    CELERY_RESULT_BACKEND=redis://localhost:6379/1
    SECRET_KEY=<your-secret-key>
    REDIS_EXPIRE_TIME=3600

    # Supabase
    SUPABASE_URL=https://<project-ref>.supabase.co
    SUPABASE_ANON_KEY=<your-anon-key>
    SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
    ```

3.  **Start Supabase Services:**

    Run the following command to start your local Supabase stack (if you are testing locally) or ensure your cloud project is running.

    ```bash
    npx supabase start
    ```

4.  **Run the Application:**

    ```bash
    uvicorn konnect.main:app --reload
    ```

    The application will be running at `http://127.0.0.1:8000`.

## 2. Testing Features

### 2.1. Authentication

**Register a new user:**

-   **Action:** Send a `POST` request to `/auth/register` with the following JSON body:

    ```json
    {
      "username": "testuser",
      "email": "test@example.com",
      "password": "password123",
      "full_name": "Test User"
    }
    ```

-   **Expected Result:** You should receive a `200 OK` response with the new user's details.

**Log in and get an access token:**

-   **Action:** Send a `POST` request to `/auth/token` with the following form data (`x-www-form-urlencoded`):

    -   `username`: `test@example.com` (note: this is the email)
    -   `password`: `password123`

-   **Expected Result:** You should receive a `200 OK` response with an `access_token`, `refresh_token`, and `token_type`.

### 2.2. Storage (Image Uploads and Optimization)

**Upload an image for a listing:**

-   **Prerequisite:** You need a valid `listing_id` and an access token for the user who owns the listing.
-   **Action:** Send a `POST` request to `/listings/{listing_id}/images` with the following:
    -   **Headers:** `Authorization: Bearer <your_access_token>`
    -   **Body:** `multipart/form-data` with one or more image files.
-   **Expected Result:** You should receive a `201 CREATED` response with the details of the uploaded image.

**Retrieve and transform an image:**

-   **Action:** Send a `GET` request to `/listings/{listing_id}/images?width=200&height=200&resize=cover`.
-   **Expected Result:** You should receive a `200 OK` response with a list of images for the listing. The `file_path` for each image will be a URL pointing to a resized and cropped version of the image.

### 2.3. Realtime

1.  **Open two terminals.**
2.  **In the first terminal, start the listener:**

    ```bash
    python scripts/realtime_demo.py
    ```

3.  **In the second terminal, send a test message:**
    -   First, update `scripts/send_test_message.py` with valid user IDs from your `profiles` table.
    -   Then, run the script:

        ```bash
        python scripts/send_test_message.py
        ```

4.  **Observe the result:** You should see the new message printed in real-time in the first terminal.

### 2.4. Edge Functions

1.  **Create an admin user:**

    ```bash
    python scripts/create_admin_user.py
    ```

    Save the `user_id` from the output.

2.  **Create a marketplace request:**
    -   Open `scripts/create_marketplace_request.py` and replace `a_valid_user_id` with the admin user ID.
    -   Run the script:

        ```bash
        python scripts/create_marketplace_request.py
        ```

    Save the `id` of the marketplace request from the output.

3.  **Invoke the Edge Function:**
    -   Open `scripts/invoke_approve_marketplace_request.py` and replace `request_id_to_approve = 1` with the ID of the marketplace request.
    -   Run the script:

        ```bash
        python scripts/invoke_approve_marketplace_request.py
        ```

4.  **Verify the result:** Check the `marketplace_requests` and `marketplaces` tables in your Supabase dashboard to confirm that the request was approved and a new marketplace was created.

### 2.5. Database RLS

Testing RLS requires making requests as different users and verifying that they can only access the data they are supposed to.

**Example Test:**

1.  Create two users, User A and User B.
2.  User A creates a new listing.
3.  Log in as User B and get an access token.
4.  Try to update or delete the listing created by User A. You should receive a `403 Forbidden` or `404 Not Found` error, as the RLS policies prevent users from modifying other users' data.
