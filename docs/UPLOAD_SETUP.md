# Invoice Upload Feature Setup

This guide explains how to set up the invoice upload feature with Vercel Blob and WebSocket integration.

## Required Packages

You'll need to install the following packages:

```bash
npm install @vercel/blob socket.io-client
# or
pnpm add @vercel/blob socket.io-client
```

## Environment Variables

Add the following environment variables to your `.env.local` file:

```env
# Vercel Blob Storage
BLOB_READ_WRITE_TOKEN=your_vercel_blob_token_here

# Backend API URL (for WebSocket connection and processing)
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
```

## Vercel Blob Setup

### Getting Your Blob Token

1. Go to [vercel.com](https://vercel.com) and sign in to your account
2. Select your project (or create a new one if needed)
3. Click on the **Storage** tab in the project dashboard
4. Click **Create Database** → Select **Blob**
5. Give your store a name (e.g., "invoice-uploads")
6. After creation, go to the **.env.local** tab or **Settings**
7. Copy the `BLOB_READ_WRITE_TOKEN` value
8. Paste it into your local `.env.local` file

**Alternative: Using Vercel CLI**

```bash
vercel blob create invoice-uploads
# Follow the prompts and it will show you the token
```

## Backend Requirements

The backend must have the following endpoints:

1. **POST /api/v1/invoices/process-batch** - Receives batch processing requests
   - Accepts: `{ files: [...], options: {...} }`
   - Returns: `{ task_ids: [...] }`

2. **WebSocket Connection** - Real-time updates via Socket.IO
   - URL: `http://localhost:5000` (same as API server)
   - Connect timeout: 5 seconds
3. **WebSocket Events**:
   - Client emits: `join_task` with `{ task_id }`
   - Server emits: `task_update` with `{ task_id, status, progress, result, error, filename }`
   - Connection events: `connect`, `disconnect`, `connect_error`

## How It Works

1. User clicks "Upload Invoices" button on dashboard
2. Modal opens with file selection and processing options
3. User selects files and configures:
   - AI Model Provider (OpenAI or Anthropic)
   - Auto-save confidence threshold (50-95%)
   - Human-in-the-loop review option
4. Files are uploaded to Vercel Blob storage
5. Backend is notified via `/process-batch` endpoint
6. WebSocket connection provides real-time updates
7. Results are displayed in real-time

## Confidence Threshold

The confidence threshold determines when extractions are auto-saved:

- **High (90-95%)**: Only very confident extractions are auto-saved
- **Medium (75-85%)**: Balanced approach
- **Low (50-70%)**: Most extractions are auto-saved

When "Human in the loop" is enabled, all extractions require manual approval regardless of confidence.

## WebSocket Events

The ProcessingContext handles these WebSocket events:

**Client Events (emitted to server):**

- `join_task` - Join a task room for updates
  ```typescript
  {
    task_id: string;
  }
  ```

**Server Events (received from server):**

- `connect` - WebSocket connected successfully
- `disconnect` - WebSocket disconnected
- `connect_error` - Connection failed (shows toast after 5s timeout)
- `task_update` - Job status update
  ```typescript
  {
    task_id: string;
    status: "pending" | "processing" | "completed" | "failed";
    progress: number; // 0-100
    result?: any;
    error?: string;
    filename?: string;
  }
  ```

**Connection Timeout:**

- If no connection is established within 5 seconds, a toast notification will appear
- This helps users know when the backend server is not running

## File Constraints

- Supported formats: PDF, PNG, JPG, JPEG, GIF, BMP, TIFF
- Maximum file size: 10MB per file
- Multiple files supported

## Testing

1. Start your backend server (make sure WebSocket support is enabled)
2. Start Next.js dev server
3. Navigate to `/dashboard`
4. Click "Upload Invoices"
5. Select test invoice files
6. Configure processing options
7. Monitor real-time updates via toast notifications

## Troubleshooting

### WebSocket not connecting

- Check `NEXT_PUBLIC_BACKEND_URL` is correct
- Ensure backend server is running
- Check browser console for connection errors

### Files not uploading

- Verify `BLOB_READ_WRITE_TOKEN` is set correctly
- Check file size (must be under 10MB)
- Ensure file format is supported

### Processing not starting

- Check backend `/process-batch` endpoint is available
- Verify file URLs are accessible from backend
- Check backend logs for errors
