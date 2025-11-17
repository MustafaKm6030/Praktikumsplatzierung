# Naming Conventions

## Overview

This document defines the naming conventions for the Praktikumsamt Management System. Consistent naming improves code readability, maintainability, and team collaboration.

---

## Git

### Branch Names

```bash
issues/5_student_crud_forms
feature/13_dashboard_statistics
bugfix/6_settings_tab_crash
docs/naming_conventions
```

**Rule**: `type/number_description_with_underscores`

Types: `issues`, `feature`, `bugfix` , `refactor` , `docs`

---

### Commit Messages

```bash
git commit -m "#15 Add: Student create form"
git commit -m "#23 Fix: Pagination error"
git commit -m "Docs: Naming conventions"
git commit -m "#2 QE: ci pipeline"
```

---

## File Naming

### Frontend (JavaScript/React)

**React Components:**

* Format: `PascalCase.jsx`
* Examples: `StudentList.jsx`, `SettingsGeneral.jsx`

**Other Files:**

* Format: `camelCase.js`
* Examples: `studentsApi.js`, `config.js`

**Tests:**

* Format: `ComponentName.test.js`
* Examples: `StudentList.test.js`

### Backend (Python/Django)

**Python Files:**

* Format: `snake_case.py`
* Examples: `models.py`, `student_service.py`

**Django Apps:**

* Format: `snake_case` (plural)
* Examples: `students/`, `teachers/`, `schools/`

**Tests:**

- Format: `test_*.py`
- Examples: `test_models.py`, `test_views.py`, `test_student_service.py`

---

## Identifier Naming

### Frontend

**Variables & Constants:**

```javascript
// Variables: camelCase, descriptive


const studentList = [];
const isFormValid = true;
const maxStudentsPerTeacher = 20;

// Constants: UPPER_SNAKE_CASE


const API_BASE_URL = 'http://localhost:8000/api';
const MAX_RETRY_ATTEMPTS = 3;

// Boolean: is/has/can prefix


const isValid = true;
const hasPermission = false;
```

**Functions:**

```javascript
// Format: camelCase, verb + noun


function fetchStudents() { }
function validateForm() { }
function calculateTotal() { }

// Boolean functions: is/has/can prefix


function isValid() { }
function hasAccess() { }
```

**React Components:**

```javascript
// Component names: PascalCase


function StudentList() { }
function SettingsGeneral() { }

// Props: camelCase


function StudentForm({ student, onSubmit, isEditMode }) { }

// Event handlers: handle prefix


const handleClick = () => { };
const handleSubmit = () => { };

// State: descriptive


const [students, setStudents] = useState([]);
const [isLoading, setIsLoading] = useState(false);
```

### Backend

**Variables & Constants:**

```python
# Variables: snake_case
student_list = []
is_form_valid = True
max_students_per_teacher = 20

# Constants: UPPER_SNAKE_CASE
MAX_STUDENTS_PER_TEACHER = 20
DEFAULT_ZONE = 1
API_BASE_URL = 'http://localhost:8000'
```

**Functions:**

```python
# Format: snake_case, verb + noun
def fetch_students():
    pass

def validate_form():
    pass

# Boolean: is/has/can prefix
def is_valid():
    pass

def has_permission():
    pass
```

**Classes:**

```python
# Format: PascalCase
class Student(models.Model):
    pass

class StudentSerializer(serializers.ModelSerializer):
    pass
```

---

## Database & API

**Database Tables:**

- Format: `snake_case`, plural
- Examples: `students`, `teachers`, `schools`, `assignments`

**Columns:**

- Format: `snake_case`
- Examples: `first_name`, `matrikelnr`, `home_address`

**API Endpoints:**

- Format: lowercase, hyphens
- Examples: `/api/students`, `/api/system-settings`

---

## Common Naming Patterns

### Avoid These Problems

**Problem 1: Multiple names for same concept (Synonyms)**

```javascript
// ❌ BAD: Synonyms for "absolute position"



const x = getPosition();
const pos = getPosition();
const apos = getPosition();
const abspos = getPosition();
const absolutePosition = getPosition();

// ✅ GOOD: One name only



const absolutePosition = getPosition();
```

**Problem 2: Same name for different concepts (Homonyms)**

```javascript
// ❌ BAD: "position" for both absolute and relative



const position = getAbsolutePosition();  // absolute
const position = getRelativePosition();  // relative (CONFLICT!)

// ✅ GOOD: Distinct names



const absolutePosition = getAbsolutePosition();
const relativePosition = getRelativePosition();
```

**Problem 3: Generic/meaningless names**

```javascript
// ❌ BAD



const p = calculatePermutation();
const data = fetchStudents();
const temp = value * 2;

// ✅ GOOD



const permutation = calculatePermutation();
const students = fetchStudents();
const doubledValue = value * 2;
```

---

## Documentation Files

```bash
README.md
NAMING_CONVENTIONS.md
SETUP_GUIDE.md
```

**Rule**: `ALL_CAPS_WITH_UNDERSCORES.md` for docs

---

## Enforcement

These conventions are enforced through:

1. **ESLint** (Frontend): Automatically checks JavaScript/React code
2. **flake8** (Backend): Checks Python code style
3. **Code Review**: Team members check during MR review
4. **TeamScale**: Monitors naming convention violations

---

## Questions?

If you're unsure about naming something:

1. Check this guide first
2. Look at similar code in the codebase
3. Ask in the team chat
4. Use your IDE's linter (it will warn you!)

---

**Last Updated**: Sprint 2, November 2025\
**Maintainer**: Team 2\
**Version**: 1.0