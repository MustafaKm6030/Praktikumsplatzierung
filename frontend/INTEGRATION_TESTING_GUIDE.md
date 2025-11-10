# Backend API Integration - Testing Guide

## Overview
This guide covers testing the integration of PL Management, Student Management, and System Settings pages with the live Django backend.

## Prerequisites

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Ensure PostgreSQL is running:
   ```bash
   cd database
   docker-compose up -d
   cd ..
   ```

3. Run migrations (if not already done):
   ```bash
   python manage.py migrate
   ```

4. Create sample data (optional but recommended):
   ```bash
   python manage.py createsuperuser
   # Access admin at http://localhost:8000/admin/ to add sample PLs, Students, Settings
   ```

5. Start the backend server:
   ```bash
   python manage.py runserver
   ```
   Backend should be running at `http://localhost:8000`

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (if not already done):
   ```bash
   npm install
   ```

3. Start the frontend server:
   ```bash
   npm start
   ```
   Frontend should be running at `http://localhost:3000`

## Testing Checklist

### ✅ Acceptance Criteria 1: All list views connected to GET APIs

#### PL Management (Teachers) Page
**URL**: `http://localhost:3000/teachers`

**Tests**:
- [ ] Page loads without errors
- [ ] Loading spinner appears during data fetch
- [ ] PL data is displayed in table format with columns:
  - PL ID
  - Name
  - Schule (School)
  - Schulart (Program - GS/MS)
  - Hauptfach (Main Subject)
  - Bevorzugte Praktika (Preferred Praktikum Types)
  - Anrechnungsstd (Credit Hours)
  - Schulamt (School Office)
  - Max. Studierende (Max Students)
  - Status (Available/Unavailable)
- [ ] Footer shows total PLs and available PLs count
- [ ] Empty state message appears if no data exists

**API Call**: `GET /api/pls/`

**Console Check**: Open browser DevTools → Network tab
- Should see successful request to `/api/pls/` with status 200
- Response should contain array of PL objects

#### Student Management Page
**URL**: `http://localhost:3000/students`

**Tests**:
- [ ] Page loads without errors
- [ ] Loading spinner appears during data fetch
- [ ] Student data is displayed in table format with columns:
  - Studenten-ID
  - Name
  - Programm (GS/MS)
  - Hauptfach (Primary Subject)
  - Zusatzfächer (Additional Subjects)
  - E-Mail
  - Heimatregion (Home Region)
  - Zone (Preferred Zone)
- [ ] Footer shows total students, GS count, and MS count
- [ ] Empty state message appears if no data exists
- [ ] Import and Export buttons are visible

**API Call**: `GET /api/students/`

**Console Check**: 
- Should see successful request to `/api/students/` with status 200
- Response should contain array of Student objects

### ✅ Acceptance Criteria 2: Search and filter controls trigger API calls

#### PL Management Search & Filters

**Search Functionality**:
- [ ] Type in search box (searches Name, E-Mail, School)
- [ ] Verify debounce delay (results update after ~500ms of stopping typing)
- [ ] Check Network tab for API call with `search` parameter
- [ ] Results update to match search term
- [ ] Clear search shows all results again

**Filter - Schulart (Program)**:
- [ ] Select "Grundschule (GS)" from dropdown
- [ ] Check Network tab for API call with `program=GS` parameter
- [ ] Table updates to show only GS PLs
- [ ] Select "Mittelschule (MS)"
- [ ] Table updates to show only MS PLs
- [ ] Select "Alle Schularten" to show all

**Filter - Schulamt** (Client-side):
- [ ] Select a specific Schulamt from dropdown
- [ ] Table filters to show only PLs from that Schulamt
- [ ] No additional API call (client-side filtering)

#### Student Management Search & Filters

**Search Functionality**:
- [ ] Type in search box (searches Name, Student ID, E-Mail)
- [ ] Verify debounce delay (~500ms)
- [ ] Check Network tab for API call with `search` parameter
- [ ] Results update to match search term

**Filter - Programm**:
- [ ] Select "Grundschule (GS)"
- [ ] Check Network tab for API call with `program=GS` parameter
- [ ] Table shows only GS students
- [ ] Select "Mittelschule (MS)"
- [ ] Table shows only MS students

**Filter - Region**:
- [ ] Select a specific region from dropdown
- [ ] Check Network tab for API call with `home_region` parameter
- [ ] Table shows only students from that region

### ✅ Acceptance Criteria 3: System Settings can load and save data

**URL**: `http://localhost:3000/settings`

#### Load Settings Test:
- [ ] Navigate to Settings page
- [ ] Loading spinner appears
- [ ] Form fields populate with data from backend:
  - Current Academic Year
  - PDP Default Deadline
  - SFP/ZSP Default Deadline
  - University Name
  - Contact Email
  - Contact Phone
  - Total Budget
  - GS Budget Percentage
  - MS Budget Percentage

**API Call**: `GET /api/settings/`

**Console Check**:
- Should see successful request to `/api/settings/` with status 200
- Response contains settings object with active settings

#### Save Settings Test:
- [ ] Modify one or more fields (e.g., change Academic Year to "2025/2026")
- [ ] Click "Save Changes" button
- [ ] Loading state appears on button ("Saving...")
- [ ] Success message appears: "Einstellungen erfolgreich gespeichert! ✅"
- [ ] Check Network tab for PATCH request to `/api/settings/{id}/`
- [ ] Page reloads data showing updated values
- [ ] Verify changes persist by refreshing the page

**Error Handling**:
- [ ] Enter invalid academic year format (e.g., "2024")
- [ ] Attempt to save
- [ ] Error message should appear from backend validation

### ✅ Acceptance Criteria 4: Clear user feedback for loading and errors

#### Loading Indicators:
- [ ] **PL Management**: Spinner shows "Lade Praktikumslehrkräfte..."
- [ ] **Student Management**: Spinner shows "Lade Studenten..."
- [ ] **Settings**: Spinner shows "Lade Einstellungen..."
- [ ] **Save Button**: Text changes to "Saving..." when clicked

#### Error Scenarios:

**Backend Not Running Test**:
1. Stop the Django backend (`Ctrl+C` in backend terminal)
2. Refresh any page (PLs, Students, or Settings)
3. Verify error banner appears with message:
   - "Network error. Please check your connection and ensure the backend is running."
4. Error banner has warning icon (⚠️)
5. Error banner has red background

**API Error Test**:
1. Navigate to `/api/pls/` in browser directly
2. Verify API is working
3. In Settings, enter invalid data (e.g., budget percentages that don't sum to 100)
4. Try to save
5. Error message should display backend validation error

### ✅ Acceptance Criteria 5: No console errors

**Console Check**:
- [ ] Open browser DevTools → Console tab
- [ ] Navigate through all pages: Dashboard, Teachers, Students, Settings
- [ ] Perform searches and filter operations
- [ ] Save settings
- [ ] Check console for:
  - ❌ No red errors (except expected network errors when testing)
  - ⚠️ Warnings are acceptable (deprecation warnings from dependencies)
  - ℹ️ Info/log messages are fine

**Common Issues to Watch**:
- Missing dependencies
- CORS errors (should not occur due to proxy configuration)
- React key warnings
- Missing props warnings

### ✅ Acceptance Criteria 6: Manual testing and code review

#### Functionality Tests:

**Export Students**:
- [ ] Click "Exportieren" button on Students page
- [ ] CSV file downloads successfully
- [ ] File name includes date: `students_export_YYYY-MM-DD.csv`
- [ ] File contains student data

**Import Students** (if backend supports):
- [ ] Click "Importieren" button
- [ ] Select a valid CSV file
- [ ] Success message appears
- [ ] Table refreshes with new data

#### Code Quality Checks:
- [ ] No console.log statements in production code (some are OK for debugging)
- [ ] Proper error handling in all API calls
- [ ] Loading states for all async operations
- [ ] Responsive design (test on different screen sizes)
- [ ] Accessible form labels and inputs


## Troubleshooting

### CORS Errors
If you see CORS errors:
1. Verify backend has `corsheaders` in INSTALLED_APPS
2. Check backend settings for CORS_ALLOWED_ORIGINS
3. Ensure proxy is configured in `frontend/package.json`

### Proxy Not Working
If API calls fail with 404:
1. Verify `"proxy": "http://localhost:8000"` in `package.json`
2. Restart frontend development server
3. Check backend is running on port 8000

### Empty Data
If pages load but show no data:
1. Access Django admin: `http://localhost:8000/admin/`
2. Add sample data for PLs, Students, and System Settings
3. Refresh frontend pages

## Success Criteria Summary

All integrations are successful when:
- ✅ All list views load data from backend APIs
- ✅ Search triggers API calls with debouncing
- ✅ Filters update API query parameters
- ✅ Settings loads and saves successfully
- ✅ Loading indicators appear during operations
- ✅ User-friendly error messages on failure
- ✅ No console errors (except during error scenario testing)
- ✅ Export/Import functionality works

## API Endpoints Reference

### PL Management
- **List PLs**: `GET /api/pls/`
  - Query params: `search`, `program`, `school`, `is_available`
- **Get PL**: `GET /api/pls/{id}/`
- **Create PL**: `POST /api/pls/`
- **Update PL**: `PUT /api/pls/{id}/` or `PATCH /api/pls/{id}/`
- **Delete PL**: `DELETE /api/pls/{id}/`

### Student Management
- **List Students**: `GET /api/students/`
  - Query params: `search`, `program`, `home_region`, `preferred_zone`
- **Get Student**: `GET /api/students/{id}/`
- **Export Students**: `GET /api/students/export/`
- **Import Students**: `POST /api/students/import_csv/`

### System Settings
- **Get Active Settings**: `GET /api/settings/`
- **Get All Settings**: `GET /api/settings/all/`
- **Get Settings by ID**: `GET /api/settings/{id}/`
- **Update Settings**: `PATCH /api/settings/{id}/`


