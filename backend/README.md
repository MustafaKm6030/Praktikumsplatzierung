# Praktikumsamt Backend

## Setup & Run

### 1. Start PostgreSQL
```bash
cd database
docker-compose up -d
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Superuser (first time only)
```bash
python manage.py createsuperuser
```
Sample Username and password:
- Username: `aspdadmin`
- Password: `aspdadmin123`

### 5. Start Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/admin/

---

## To Stop Database
```bash
cd database
docker-compose down
```

## Run Tests
```bash
python manage.py test
```

## Apps Structure
- `subjects/` - Subject & PraktikumType models
- `schools/` - School model
- `praktikums_lehrkraft/` - PL models
- `students/` - Student models
- `system_settings/` - System configuration
- `assignments/` - Assignment algorithm (future)
