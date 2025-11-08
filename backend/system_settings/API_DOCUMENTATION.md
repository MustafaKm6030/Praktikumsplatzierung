# System Settings API

## Overview
This API handles system-wide configuration for the Praktikumsamt application. It manages academic year settings, budget allocation between GS and MS programs, university information, and key deadlines.

Base URL: `/api/settings/`

## Endpoints

### 1. Get Active Settings
**GET /api/settings/**

Returns the currently active system settings.

#### Request
```http
GET /api/settings/
```

#### Response (200 OK)
```json
{
  "id": 1,
  "current_academic_year": "2024/2025",
  "total_anrechnungsstunden_budget": "210.00",
  "gs_budget_percentage": "80.48",
  "ms_budget_percentage": "19.52",
  "gs_budget_hours": 169.008,
  "ms_budget_hours": 40.992,
  "pdp_i_demand_deadline": "2024-12-15",
  "pl_assignment_deadline": "2025-01-31",
  "winter_semester_adjustment_date": null,
  "university_name": "Universität Passau",
  "contact_email": "praktikum@uni-passau.de",
  "contact_phone": "+49851509",
  "is_active": true,
  "created_at": "2024-11-08T10:00:00Z",
  "updated_at": "2024-11-08T10:00:00Z"
}
```

**Notes:**
- If no settings exist, the system will create default settings automatically
- Returns only the currently active academic year
- Response includes computed fields for budget hours

### 2. Get Specific Settings by ID
**GET /api/settings/{id}/**

Retrieves specific settings by ID.

#### Request
```http
GET /api/settings/1/
```

#### Response (200 OK)
Same format as Get Active Settings

**Error Responses:**
- 404 Not Found - Settings with specified ID doesn't exist

### 3. Create New Settings
**POST /api/settings/**

Creates new academic year settings.

#### Request
```http
POST /api/settings/
Content-Type: application/json

{
  "current_academic_year": "2025/2026",
  "total_anrechnungsstunden_budget": 220.0,
  "gs_budget_percentage": 81.0,
  "ms_budget_percentage": 19.0,
  "university_name": "Universität Passau",
  "contact_email": "praktikum@uni-passau.de",
  "contact_phone": "+49851509",
  "pdp_i_demand_deadline": "2025-12-15",
  "pl_assignment_deadline": "2026-01-31",
  "is_active": false
}
```

#### Required Fields
- `current_academic_year` - Format: "YYYY/YYYY" (e.g., "2024/2025")
- `total_anrechnungsstunden_budget` - Decimal
- `gs_budget_percentage` - Decimal (0-100)
- `ms_budget_percentage` - Decimal (0-100)
- `university_name` - String

#### Optional Fields
- `contact_email` - Email
- `contact_phone` - String
- `pdp_i_demand_deadline` - Date (YYYY-MM-DD)
- `pl_assignment_deadline` - Date (YYYY-MM-DD)
- `winter_semester_adjustment_date` - Date (YYYY-MM-DD)
- `is_active` - Boolean (default: false)

**Validation Rules:**
1. Academic year must be in format "YYYY/YYYY" (e.g., "2024/2025")
2. Second year must be exactly one year after the first
3. GS and MS budget percentages must sum to 100%
4. If is_active is set to true, all other settings will be deactivated

**Response:** 201 Created - Returns the created settings object

**Error Responses:**
- 400 Bad Request - Validation error with details in response body

### 4. Update Settings (Full Update)
**PUT /api/settings/{id}/**

Updates all fields of existing settings.

#### Request
```http
PUT /api/settings/1/
Content-Type: application/json

{
  "current_academic_year": "2024/2025",
  "total_anrechnungsstunden_budget": 215.0,
  "gs_budget_percentage": 82.0,
  "ms_budget_percentage": 18.0,
  "university_name": "Universität Passau",
  "contact_email": "updated@uni-passau.de",
  "contact_phone": "+49851509999",
  "is_active": true
}
```

**Notes:**
- All required fields must be provided
- Same validation rules as Create endpoint
- Setting is_active to true will deactivate all other settings

**Response:** 200 OK - Returns the updated settings object

**Error Responses:**
- 400 Bad Request - Validation error
- 404 Not Found - Settings not found

### 5. Update Settings (Partial Update)
**PATCH /api/settings/{id}/**

Updates only specified fields.

#### Request
```http
PATCH /api/settings/1/
Content-Type: application/json

{
  "contact_email": "newemail@uni-passau.de",
  "contact_phone": "+49851509999"
}
```

**Notes:**
- Only the provided fields will be updated
- Other fields remain unchanged
- Validation rules apply to any modified fields

**Response:** 200 OK - Returns the updated settings object

### 6. Delete Settings
**DELETE /api/settings/{id}/**

Deletes settings from database.

#### Request
```http
DELETE /api/settings/1/
```

**Important:** You cannot delete active settings. Activate another setting first before deleting.

**Response:** 204 No Content
```json
{
  "message": "Settings deleted successfully"
}
```

**Error Responses:**
- 400 Bad Request - Attempting to delete active settings
- 404 Not Found - Settings not found

## Custom Endpoints

### 7. Get All Settings
**GET /api/settings/all/**

Returns all settings (historical and current).

#### Request
```http
GET /api/settings/all/
```

#### Response (200 OK)
```json
[
  {
    "id": 2,
    "current_academic_year": "2024/2025",
    "is_active": true,
    ...
  },
  {
    "id": 1,
    "current_academic_year": "2023/2024",
    "is_active": false,
    ...
  }
]
```

**Notes:**
- Returns an array of all settings
- Ordered by academic year, most recent first
- Useful for viewing historical configurations

### 8. Get Budget Allocation
**GET /api/settings/{id}/budget_allocation/**

Returns calculated budget distribution details.

#### Request
```http
GET /api/settings/1/budget_allocation/
```

#### Response (200 OK)
```json
{
  "total_budget": 210.0,
  "gs_percentage": 80.48,
  "ms_percentage": 19.52,
  "gs_hours": 169.008,
  "ms_hours": 40.992
}
```

**Notes:**
- Calculates GS and MS budget hours based on percentages
- Used for budget planning and reporting

### 9. Activate Academic Year
**POST /api/settings/activate/**

Activates a specific academic year.

#### Request
```http
POST /api/settings/activate/
Content-Type: application/json

{
  "academic_year": "2024/2025"
}
```

#### Required Fields
- `academic_year` - String in format "YYYY/YYYY"

**Behavior:**
1. Deactivates all existing settings
2. Activates the specified academic year
3. Returns the activated settings object

**Response:** 200 OK - Returns the activated settings object

**Error Responses:**
- 400 Bad Request - Missing academic_year parameter
- 404 Not Found - Settings for specified year not found

## Data Models

### SystemSettings Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Auto | Primary key |
| current_academic_year | String(20) | Yes | Format: "YYYY/YYYY" |
| total_anrechnungsstunden_budget | Decimal(6,2) | Yes | Total credit hours budget |
| gs_budget_percentage | Decimal(5,2) | Yes | GS allocation % (0-100) |
| ms_budget_percentage | Decimal(5,2) | Yes | MS allocation % (0-100) |
| pdp_i_demand_deadline | Date | No | PDP I demand deadline |
| pl_assignment_deadline | Date | No | PL assignment deadline |
| winter_semester_adjustment_date | Date | No | Winter semester adjustment |
| university_name | String(200) | Yes | University name |
| contact_email | Email | No | Contact email |
| contact_phone | String(50) | No | Contact phone |
| is_active | Boolean | No | Is active year? (default: false) |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

### Computed Fields (Read-Only)
- `gs_budget_hours` - Float - Calculated as: total_budget × gs_percentage / 100
- `ms_budget_hours` - Float - Calculated as: total_budget × ms_percentage / 100

## Business Rules

### 1. Single Active Setting
- Only one academic year can be active at a time
- Setting `is_active=true` automatically deactivates all others

### 2. Budget Validation
- GS + MS percentages must equal 100% (small floating point differences allowed)

### 3. Academic Year Format
- Must be in "YYYY/YYYY" format
- Second year must be exactly first year + 1
- Valid: "2024/2025", Invalid: "2024-2025" or "2024/2026"

### 4. Delete Protection
- You cannot delete the currently active academic year
- Activate another year first, then delete

### 5. Auto-Creation
- If no settings exist, GET /api/settings/ will automatically create default settings

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"],
  "budget_percentages": ["GS and MS budget percentages must sum to 100%. Current sum: 95.0%"]
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Testing Examples

### Using curl

#### Get Active Settings
```bash
curl http://localhost:8000/api/settings/
```

#### Create Settings
```bash
curl -X POST http://localhost:8000/api/settings/ \
  -H "Content-Type: application/json" \
  -d '{
    "current_academic_year": "2025/2026",
    "total_anrechnungsstunden_budget": 220.0,
    "gs_budget_percentage": 80.0,
    "ms_budget_percentage": 20.0,
    "university_name": "Universität Passau"
  }'
```

#### Update Settings
```bash
curl -X PUT http://localhost:8000/api/settings/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "current_academic_year": "2024/2025",
    "total_anrechnungsstunden_budget": 215.0,
    "gs_budget_percentage": 80.0,
    "ms_budget_percentage": 20.0,
    "university_name": "Universität Passau"
  }'
```

#### Partial Update
```bash
curl -X PATCH http://localhost:8000/api/settings/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "contact_email": "new@uni-passau.de"
  }'
```

#### Delete Settings
```bash
curl -X DELETE http://localhost:8000/api/settings/1/
```

#### Activate Year
```bash
curl -X POST http://localhost:8000/api/settings/activate/ \
  -H "Content-Type: application/json" \
  -d '{"academic_year": "2024/2025"}'
```