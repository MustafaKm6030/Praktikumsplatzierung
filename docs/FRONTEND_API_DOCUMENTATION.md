# Frontend API Documentation

This document provides all API endpoints needed for the Schools, Students, Teachers (PLs), and Allocation pages buttons.

## Base URL

All API endpoints use the base URL: `http://malik08.stud.fim.uni-passau.de/api/`

---

## Schools Management APIs

### 1. List All Schools
**GET** `/api/schools/`

Returns a list of all schools with pagination and filtering support.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Grundschule Musterstadt",
    "school_type": "GS",
    "city": "Musterstadt",
    "district": "District 1",
    "zone": 1,
    "opnv_code": "4a",
    "is_active": true,
    "distance_km": 5.2,
    "latitude": 48.5734,
    "longitude": 13.4591
  }
]
```

### 2. Get Single School Details
**GET** `/api/schools/{id}/`

Returns detailed information about a specific school.

**Response:**
```json
{
  "id": 1,
  "name": "Grundschule Musterstadt",
  "school_type": "GS",
  "city": "Musterstadt",
  "district": "District 1",
  "zone": 1,
  "opnv_code": "4a",
  "is_active": true,
  "distance_km": 5.2,
  "latitude": 48.5734,
  "longitude": 13.4591,
  "notes": "Additional notes about the school",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create New School
**POST** `/api/schools/`

Creates a new school record.

**Request Body:**
```json
{
  "name": "Neue Grundschule",
  "school_type": "GS",
  "city": "Passau",
  "district": "District 2",
  "zone": 2,
  "opnv_code": "4b",
  "distance_km": 3.5,
  "is_active": true,
  "notes": "New school opening",
  "latitude": 48.5734,
  "longitude": 13.4591
}
```

**Response:**
```json
{
  "id": 15,
  "name": "Neue Grundschule",
  "school_type": "GS",
  "city": "Passau",
  "district": "District 2",
  "zone": 2,
  "opnv_code": "4b",
  "distance_km": 3.5,
  "is_active": true,
  "notes": "New school opening",
  "latitude": 48.5734,
  "longitude": 13.4591
}
```

### 4. Update School (Full Update)
**PUT** `/api/schools/{id}/`

Updates all fields of an existing school.

**Request Body:** Same as Create New School

**Response:** Updated school object (same format as Get Single School)

### 5. Update School (Partial Update)
**PATCH** `/api/schools/{id}/`

Updates only specified fields of an existing school.

**Request Body:**
```json
{
  "is_active": false,
  "notes": "School temporarily closed"
}
```

**Response:** Updated school object

### 6. Delete School
**DELETE** `/api/schools/{id}/`

Permanently deletes a school from the database.

**Response:**
```json
{
  "message": "School deleted successfully"
}
```

### 7. Import Schools from CSV
**POST** `/api/schools/import_csv/`

Uploads a CSV file to bulk create or update schools.

**Request:**
- Content-Type: `multipart/form-data`
- Field name: `file`
- File type: CSV

**CSV Format:**
```
name,school_type,city,district,zone,opnv_code,distance_km,is_active,notes,latitude,longitude
Grundschule Test,GS,Passau,District 1,1,4a,5.2,true,Test school,48.5734,13.4591
```

**Response:**
```json
{
  "created": 5,
  "updated": 3,
  "errors": [
    "Row 8: name is required"
  ]
}
```

### 8. Export Schools to CSV
**GET** `/api/schools/export/`

Downloads all schools data as a CSV file.

**Response:** CSV file download with filename `schools_export.csv`

---

## Students Management APIs

### 1. List All Students
**GET** `/api/students/students/`

Returns a list of all students with pagination and filtering support.

**Response:**
```json
[
  {
    "id": 1,
    "student_id": "S12345",
    "first_name": "Max",
    "last_name": "Mustermann",
    "email": "max.mustermann@student.de",
    "program": "GS",
    "primary_subject_name": "Mathematik",
    "zsp_subject_name": "Deutsch",
    "placement_status": "UNPLACED",
    "home_region": "Passau"
  }
]
```

### 2. Get Single Student Details
**GET** `/api/students/students/{id}/`

Returns detailed information about a specific student.

**Response:**
```json
{
  "id": 1,
  "student_id": "S12345",
  "first_name": "Max",
  "last_name": "Mustermann",
  "email": "max.mustermann@student.de",
  "phone": "+49123456789",
  "program": "GS",
  "major": "Lehramt Grundschule",
  "enrollment_date": "2023-10-01",
  "primary_subject_name": "Mathematik",
  "didactic_subject_1_name": "Deutsch",
  "didactic_subject_2_name": "Sport",
  "didactic_subject_3_name": "Englisch",
  "home_address": "Musterstraße 1, Passau",
  "semester_address": "Studentenweg 5, Passau",
  "home_region": "Passau",
  "preferred_zone": "1",
  "pdp1_completed_date": "2024-03-15",
  "pdp2_completed_date": null,
  "sfp_completed_date": null,
  "zsp_completed_date": null,
  "placement_status": "UNPLACED",
  "notes": "Student notes",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create New Student
**POST** `/api/students/students/`

Creates a new student record.

**Request Body:**
```json
{
  "student_id": "S67890",
  "first_name": "Anna",
  "last_name": "Schmidt",
  "email": "anna.schmidt@student.de",
  "phone": "+49123456789",
  "program": "MS",
  "major": "Lehramt Mittelschule",
  "home_region": "München",
  "preferred_zone": "2",
  "placement_status": "UNPLACED"
}
```

**Response:** Created student object (same format as Get Single Student)

### 4. Update Student (Full Update)
**PUT** `/api/students/students/{id}/`

Updates all fields of an existing student.

**Request Body:** Same as Create New Student

**Response:** Updated student object

### 5. Update Student (Partial Update)
**PATCH** `/api/students/students/{id}/`

Updates only specified fields of an existing student.

**Request Body:**
```json
{
  "placement_status": "PLACED",
  "pdp1_completed_date": "2024-03-15"
}
```

**Response:** Updated student object

### 6. Delete Student
**DELETE** `/api/students/students/{id}/`

Permanently deletes a student from the database.

**Response:**
```json
{
  "message": "Student deleted successfully"
}
```

### 7. Import Students from CSV
**POST** `/api/students/students/import_csv/`

Uploads a CSV file to bulk create or update students.

**Request:**
- Content-Type: `multipart/form-data`
- Field name: `file`
- File type: CSV

**CSV Format:**
```
student_id,first_name,last_name,email,phone,program,major,enrollment_date,primary_subject_code,didactic_subject_1_code,didactic_subject_2_code,didactic_subject_3_code,home_address,semester_address,home_region,preferred_zone,pdp1_completed_date,pdp2_completed_date,sfp_completed_date,zsp_completed_date,placement_status,notes
S12345,Max,Mustermann,max@student.de,+49123,GS,Lehramt GS,2023-10-01,MAT,DEU,SPO,ENG,Musterstr 1,Studentenweg 5,Passau,1,2024-03-15,,,,UNPLACED,Notes here
```

**Response:**
```json
{
  "created": 10,
  "updated": 5,
  "errors": [
    "Row 12: email is required"
  ]
}
```

### 8. Export Students to CSV
**GET** `/api/students/students/export/`

Downloads all students data as a CSV file.

**Response:** CSV file download with filename `students_export.csv`

---

## Teachers (Praktikumslehrkräfte) Management APIs

### 1. List All Teachers
**GET** `/api/pls/`

Returns a list of all Praktikumslehrkräfte with pagination and filtering support.

**Response:**
```json
[
  {
    "id": 1,
    "first_name": "Maria",
    "last_name": "Müller",
    "email": "maria.mueller@school.de",
    "phone": "+49123456789",
    "school": 5,
    "school_name": "Grundschule Musterstadt",
    "program": "GS",
    "program_display": "Grundschule",
    "anrechnungsstunden": 2.0,
    "schulamt": "Passau",
    "capacity": 2,
    "is_active": true,
    "main_subject": 3,
    "available_subjects": [1, 2, 3],
    "main_subject_name": "Mathematik",
    "preferred_praktika_raw": "PDP I, SFP"
  }
]
```

### 2. Get Single Teacher Details
**GET** `/api/pls/{id}/`

Returns detailed information about a specific teacher.

**Response:**
```json
{
  "id": 1,
  "first_name": "Maria",
  "last_name": "Müller",
  "email": "maria.mueller@school.de",
  "phone": "+49123456789",
  "school": 5,
  "school_detail": {
    "id": 5,
    "name": "Grundschule Musterstadt",
    "school_type": "GS",
    "city": "Passau"
  },
  "program": "GS",
  "program_display": "Grundschule",
  "main_subject": 3,
  "main_subject_name": "Mathematik",
  "available_praktikum_types_display": [
    {
      "id": 1,
      "code": "PDP_I",
      "name": "PDP I"
    },
    {
      "id": 3,
      "code": "SFP",
      "name": "SFP"
    }
  ],
  "available_subjects_display": [
    {
      "id": 1,
      "code": "MAT",
      "name": "Mathematik"
    },
    {
      "id": 2,
      "code": "DEU",
      "name": "Deutsch"
    }
  ],
  "schulamt": "Passau",
  "anrechnungsstunden": 2.0,
  "capacity": 2,
  "preferred_praktika_raw": "PDP I, SFP",
  "current_year_notes": "Available for winter semester",
  "is_active": true,
  "notes": "Preferred subjects: Math, German",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create New Teacher
**POST** `/api/pls/`

Creates a new Praktikumslehrkraft record.

**Request Body:**
```json
{
  "first_name": "Peter",
  "last_name": "Weber",
  "email": "peter.weber@school.de",
  "phone": "+49987654321",
  "school": 5,
  "program": "MS",
  "main_subject": 2,
  "available_praktikum_types": [1, 2],
  "available_subjects": [1, 2, 3],
  "schulamt": "Passau",
  "anrechnungsstunden": 3.0,
  "preferred_praktika_raw": "PDP I, PDP II",
  "is_active": true
}
```

**Response:** Created teacher object (same format as Get Single Teacher)

### 4. Update Teacher (Full Update)
**PUT** `/api/pls/{id}/`

Updates all fields of an existing teacher.

**Request Body:** Same as Create New Teacher

**Response:** Updated teacher object

### 5. Update Teacher (Partial Update)
**PATCH** `/api/pls/{id}/`

Updates only specified fields of an existing teacher.

**Request Body:**
```json
{
  "is_active": false,
  "current_year_notes": "On leave this semester"
}
```

**Response:** Updated teacher object

### 6. Delete Teacher
**DELETE** `/api/pls/{id}/`

Permanently deletes a teacher from the database.

**Response:**
```json
{
  "message": "PL deleted successfully"
}
```

### 7. Import Teachers from CSV
**POST** `/api/pls/import_csv/`

Uploads a CSV file to bulk create or update teachers.

**Request:**
- Content-Type: `multipart/form-data`
- Field name: `file`
- File type: CSV

**CSV Format:**
```
first_name,last_name,email,phone,school_name,program,main_subject_code,schulamt,anrechnungsstunden,praktikum_types,available_subjects,preferred_praktika_raw,current_year_notes,is_active,notes
Maria,Müller,maria@school.de,+49123,Grundschule Musterstadt,GS,MAT,Passau,2.0,"PDP_I,SFP","MAT,DEU",PDP I preferred,Available,true,Good mentor
```

**Response:**
```json
{
  "created": 8,
  "updated": 4,
  "errors": [
    "Row 7: email is required",
    "Row 10: School 'Unknown School' not found"
  ]
}
```

### 8. Export Teachers to CSV
**GET** `/api/pls/export/`

Downloads all teachers data as a CSV file.

**Response:** CSV file download with filename `pls_export.csv`

---

## Allocation Page APIs

### 1. Get Demand Preview
**GET** `/api/assignments/demand-preview/`

Returns summary of student demand vs teacher supply for allocation planning.

**Response:**
```json
{
  "summary_cards": {
    "total_demand_slots": 150,
    "total_pl_capacity_slots": 140,
    "total_pdp_demand": 80,
    "total_wednesday_demand": 70
  },
  "detailed_breakdown": [
    {
      "practicum_type": "PDP_I",
      "program_type": "GS",
      "subject_code": "N/A",
      "subject_display_name": "N/A",
      "required_slots": 45,
      "available_pls": 40
    },
    {
      "practicum_type": "SFP",
      "program_type": "GS",
      "subject_code": "MAT",
      "subject_display_name": "Mathematik",
      "required_slots": 25,
      "available_pls": 20
    }
  ]
}
```

### 2. Run Allocation Solver
**POST** `/api/assignments/run-solver/`

Executes the optimization algorithm to generate assignments.

**Request Body:** Empty (no body required)

**Response:**
```json
{
  "status": "SUCCESS",
  "assignments": [
    {
      "mentor_name": "Müller, Maria",
      "practicum_type": "PDP_I",
      "subject": "Mathematik"
    },
    {
      "mentor_name": "Weber, Peter",
      "practicum_type": "SFP",
      "subject": "Deutsch"
    }
  ],
  "unassigned": [
    {
      "id": 15,
      "name": "Schmidt, Anna",
      "email": "anna.schmidt@school.de",
      "reason": "No available capacity",
      "school": "Mittelschule Test"
    }
  ],
  "total_assignments": 135,
  "total_unassigned": 5
}
```

### 3. Get All Assignments (Check Draft Allocation)
**GET** `/api/assignments/`

Returns all generated assignments for review in the results table.

**Response:**
```json
[
  {
    "id": 1,
    "student_id": null,
    "student_name": null,
    "practicum_type": "PDP I",
    "subject": "MAT",
    "mentor_name": "Müller, Maria",
    "school_name": "Grundschule Musterstadt",
    "status": "ok"
  },
  {
    "id": 2,
    "student_id": null,
    "student_name": null,
    "practicum_type": "SFP",
    "subject": "DEU",
    "mentor_name": "Weber, Peter",
    "school_name": "Mittelschule Test",
    "status": "ok"
  }
]
```

### 4. Update Assignment (Adjust/Edit)
**PATCH** `/api/assignments/{assignment_id}/update/`

Allows manual adjustment of assignment fields.

**Request Body:**
```json
{
  "mentor_id": 5,
  "school_id": 3,
  "subject_id": 2,
  "practicum_type_id": 1
}
```

Note: All fields are optional. Only include fields you want to update.

**Response:**
```json
{
  "success": true,
  "assignment_id": 1
}
```

**Error Response:**
```json
{
  "error": "Mentor not found"
}
```

### 5. Export Assignments to Excel
**GET** `/api/assignments/export/excel/`

Downloads all assignments as an Excel file.

**Response:** Excel file download with filename `praktikumszuteilungen.xlsx`

### 6. Export Assignments to PDF
**GET** `/api/assignments/export/pdf/`

Downloads all assignments as a PDF report.

**Response:** PDF file download with filename `praktikumszuteilungen.pdf`

---

## Error Responses

All APIs follow consistent error response format:

**400 Bad Request:**
```json
{
  "error": "Detailed error message"
}
```

**404 Not Found:**
```json
{
  "error": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error message"
}
```

---

## Notes for Frontend Developers

1. **Authentication:** Add authentication headers if required by your backend setup.

2. **File Uploads:** For CSV import endpoints, use `FormData` with the field name `file`:
   ```javascript
   const formData = new FormData();
   formData.append('file', fileObject);
   ```

3. **CSV Download:** The export endpoints return CSV files as downloads. Handle them using:
   ```javascript
   const blob = new Blob([response.data], { type: 'text/csv' });
   const url = window.URL.createObjectURL(blob);
   const link = document.createElement('a');
   link.href = url;
   link.download = 'filename.csv';
   link.click();
   ```

4. **Filtering and Search:** Most list endpoints support query parameters:
   - `?search=term` - Search across multiple fields
   - `?program=GS` - Filter by program
   - `?is_active=true` - Filter by active status
   - `?ordering=-created_at` - Sort by field (use `-` for descending)

5. **Pagination:** List endpoints return paginated results. Use `?page=2&page_size=50` to control pagination.

6. **IDs:** All resource IDs are integers. Subject IDs, School IDs, etc., should be passed as integers in request bodies.

