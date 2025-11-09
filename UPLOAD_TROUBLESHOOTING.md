# Upload Troubleshooting Guide

## Issue: "Upload Failed" Error

### Fixed Issues ✅
1. **FormData format mismatch** - Frontend now correctly sends files as a list
2. **Better error messages** - Now shows specific error details from backend
3. **Grouped uploads** - PDFs and Excel files are uploaded separately to correct endpoints

### How to Test the Fix

1. **Start Backend**
   ```bash
   cd "z:\PROJECTS  APP\stocks analyzer\PulseCompass\backend"
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend**
   ```bash
   cd "z:\PROJECTS  APP\stocks analyzer\PulseCompass"
   npm run dev
   ```

3. **Test Upload**
   - Go to http://localhost:3000
   - Navigate to Overview tab
   - Drag & drop or click to upload:
     - PDF files (transcripts)
     - Excel files (.xlsx, .xls)
     - CSV files

### Common Issues & Solutions

#### 1. Backend Not Running
**Symptom**: "Failed to fetch" or "Network error"

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, start it:
cd backend
python -m uvicorn main:app --reload --port 8000
```

#### 2. CORS Error
**Symptom**: "CORS policy" error in browser console

**Solution**: Backend already has CORS enabled. Check that:
- Backend is running on port 8000
- Frontend is running on port 3000
- No other service is using these ports

#### 3. File Format Not Supported
**Symptom**: "File is not supported" error

**Supported Formats**:
- PDFs: `.pdf`
- Excel: `.xlsx`, `.xls`
- CSV: `.csv`

#### 4. File Too Large
**Symptom**: Upload hangs or fails

**Solution**: Check file size limits in backend:
```python
# In main.py, increase if needed:
app.add_middleware(
    CORSMiddleware,
    # ... other settings
    max_age=3600,
)
```

#### 5. Missing Dependencies
**Symptom**: "Module not found" errors in backend

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### Debug Mode

#### Check Backend Logs
The backend terminal will show detailed error messages:
```
INFO:     127.0.0.1:52000 - "POST /upload/excel HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
```

#### Check Browser Console
Open DevTools (F12) → Console tab to see:
- Network requests
- Error messages
- Response data

#### Test Upload Endpoint Directly
```bash
# Test with curl
curl -X POST http://localhost:8000/upload/excel \
  -F "files=@path/to/your/file.xlsx"
```

### Expected Behavior

#### Successful Upload
1. File is uploaded to backend
2. Backend processes the file (parses Excel/PDF)
3. Backend returns success response with file_id
4. Frontend shows green toast: "X file(s) uploaded and processed successfully"
5. File appears in uploaded files list

#### Failed Upload
1. Backend returns error response
2. Frontend shows red toast with specific error message
3. Error is logged to browser console
4. No file is added to the list

### File Processing

#### PDF Files
- Extracted text using PyPDF2/pdfplumber
- Analyzed for management integrity
- Scored 0-10
- Stored in `app.state.processed_files`

#### Excel/CSV Files
- Parsed using pandas
- Metrics calculated (ROE, ROA, etc.)
- Traffic lights generated
- Philosophy scores computed
- Stored in `app.state.processed_files`

### API Response Format

#### Success Response
```json
{
  "success": true,
  "message": "Successfully processed 1 Excel files",
  "files": [
    {
      "file_id": "excel_1",
      "filename": "company_financials.xlsx",
      "status": "processed",
      "metrics": { ... }
    }
  ]
}
```

#### Error Response
```json
{
  "detail": "File company_financials.txt is not supported"
}
```

### Next Steps After Upload

1. **View Analysis**: Uploaded files are processed and stored
2. **Check Metrics**: Financial metrics are calculated
3. **Philosophy Scores**: Investment philosophy scores are generated
4. **Charts**: Data is available for visualization

### Still Having Issues?

1. **Check both terminals** (backend and frontend) for errors
2. **Verify file format** is supported
3. **Try a smaller file** to rule out size issues
4. **Check network tab** in DevTools for actual error response
5. **Restart both services** (backend and frontend)

---

**The upload functionality has been fixed and should now work correctly!** 🎉
