# Quick Start Guide - Backend Integration

## 🚀 Starting the Application

### Backend (Terminal 1)
```bash
cd backend
python manage.py runserver
```
Backend runs at: `http://localhost:8000`

### Frontend (Terminal 2)
```bash
cd frontend
npm start
```
Frontend runs at: `http://localhost:3000`

## 📋 Accessing the Pages

- **PL Management**: http://localhost:3000/teachers
- **Student Management**: http://localhost:3000/students
- **System Settings**: http://localhost:3000/settings
- **Dashboard**: http://localhost:3000/

## ✅ What's Integrated

### PL Management (Teachers) ✅
- Live data from `/api/pls/`
- Search by name, email, school
- Filter by Schulart (GS/MS) and Schulamt
- Loading indicators and error handling
- Summary statistics

### Student Management ✅
- Live data from `/api/students/`
- Search by name, ID, email
- Filter by Program (GS/MS) and Region
- Import/Export functionality
- Loading indicators and error handling
- Summary statistics

### System Settings ✅
- Load from `/api/settings/`
- Save with `/api/settings/{id}/`
- All fields including budget allocation
- Loading and save states
- Success/error feedback

## 🧪 Testing

See `frontend/INTEGRATION_TESTING_GUIDE.md` for comprehensive testing checklist.

**Quick Test**:
1. Start both servers
2. Navigate to each page
3. Verify data loads
4. Try search and filters
5. Check console for errors (should be clean)

## 📝 Documentation

- **Testing Guide**: `frontend/INTEGRATION_TESTING_GUIDE.md`
- **API Documentation**: `backend/system_settings/API_DOCUMENTATION.md`

## ⚠️ Prerequisites

Make sure you have:
- ✅ PostgreSQL running (for backend)
- ✅ Python dependencies installed (`pip install -r requirements.txt`)
- ✅ Node dependencies installed (`npm install` in frontend/)
- ✅ Backend migrations run (`python manage.py migrate`)
- ✅ Sample data created (via Django admin or fixtures)

## 🔧 Troubleshooting

**No data showing?**
- Access Django admin: http://localhost:8000/admin/
- Add sample PLs, Students, and Settings

**API errors?**
- Check backend is running on port 8000
- Verify proxy in `frontend/package.json`

**CORS issues?**
- Should not occur with proxy setup
- If they do, check backend CORS settings

## 📊 Acceptance Criteria - All Met ✅

1. ✅ All list views connected to GET APIs
2. ✅ Search and filters trigger API calls
3. ✅ Settings can load and save data
4. ✅ Loading indicators and error messages
5. ✅ No console errors
6. ✅ Manually tested and reviewed

## 🎯 Next Steps

Optional enhancements:
- Add pagination for large datasets
- Implement Schools Management page
- Add automated tests
- Implement user authentication
- Add data visualization

