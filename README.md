# 🏥 Hospital Management System

A professional, secure, and modular **Hospital Infrastructure Management System** designed for internal hospital use on secure local networks. Built with FastAPI, SQLAlchemy, vanilla JavaScript, and SQLite/MySQL.

## ✨ Features

### Core Modules
- **📊 Dashboard** - Real-time hospital overview with key metrics
- **👥 Patient Management** - Full CRUD with search, filters, and pagination
- **📋 Medical Reports** - Create, edit, and manage patient medical records
- **🔬 Diagnosis Assistance** - Symptom matching against medical knowledge database
- **🤖 AI Integration** - AI-powered report summarization and recommendations
- **📄 Discharge Reports** - Professional PDF generation with ReportLab
- **📚 Patient History** - Comprehensive timeline of all medical events
- **📝 Access Logs** - Full audit trail with search and CSV export
- **⚙️ Settings** - Profile management and password change

### Security
- **JWT Authentication** - Token-based secure authentication
- **bcrypt Password Hashing** - Industry-standard password security
- **Role-Based Access Control** - Admin, Doctor, Staff roles
- **Secure Headers** - XSS, CSRF, clickjacking protection
- **Input Validation** - All inputs validated via Pydantic
- **SQL Injection Protection** - SQLAlchemy ORM prevents injection
- **Session Timeout** - Configurable JWT expiration
- **Account Locking** - Failed login attempt tracking

## 🏗️ Architecture

```
hospital-management/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── models/            # SQLAlchemy ORM models (8 tables)
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── routers/           # REST API endpoints (7 modules)
│   │   ├── services/          # Business logic layer
│   │   ├── middleware/        # Auth, security middleware
│   │   ├── utils/             # JWT, bcrypt utilities
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # Database connection
│   │   ├── main.py            # FastAPI application
│   │   ├── seed.py            # Database seeder
│   │   └── tests.py           # Test suite (12 tests)
│   └── requirements.txt
├── frontend/                   # HTML/CSS/JavaScript frontend
│   ├── css/                   # Stylesheets (3 files)
│   ├── js/                    # JavaScript modules (10 files)
│   ├── pages/                 # HTML pages (10 pages)
│   └── index.html             # Landing page
├── start.sh                   # One-click start script
├── .gitignore
└── README.md
```

### Database Schema

| Table | Description |
|-------|-------------|
| `users` | System users with roles (admin/doctor/staff) |
| `patients` | Patient demographics and medical info |
| `medical_reports` | Doctor-created medical reports |
| `ai_summaries` | AI-generated summaries of reports |
| `diagnosis_database` | Knowledge base of conditions and symptoms |
| `diagnoses` | Patient-specific diagnoses |
| `discharge_reports` | Discharge summaries with PDF paths |
| `access_logs` | Complete audit trail of all actions |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/hospital-management.git
cd hospital-management

# 2. Make start script executable
chmod +x start.sh

# 3. Run the setup and start the server
./start.sh
```

The server will start at **http://localhost:8000** with API docs at **http://localhost:8000/api/docs**.

### Manual Setup

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Initialize database and seed data
cd backend
python3 -c "from app.database import init_db; init_db()"
python3 -m app.seed

# 3. Start the server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Doctor** | `doctor1` | `doctor123` |
| **Staff** | `staff1` | `staff123` |

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with username/password |
| POST | `/api/auth/logout` | Logout (logs activity) |
| POST | `/api/auth/register` | Register new user (admin only) |
| GET | `/api/auth/me` | Get current user profile |
| GET | `/api/auth/users` | List all users (admin only) |
| PUT | `/api/auth/change-password` | Change password |

### Patients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/patients` | List patients (search, filter, paginate) |
| GET | `/api/patients/{id}` | Get patient details |
| POST | `/api/patients` | Create patient |
| PUT | `/api/patients/{id}` | Update patient |
| DELETE | `/api/patients/{id}` | Delete patient (admin only) |

### Medical Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports` | List reports |
| GET | `/api/reports/{id}` | Get report details |
| POST | `/api/reports` | Create report (doctor+) |
| PUT | `/api/reports/{id}` | Update report (doctor+) |
| DELETE | `/api/reports/{id}` | Delete report (admin) |

### AI Integration
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/summarize/{report_id}` | Generate AI summary for report |

### Diagnosis
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/diagnosis/database` | List diagnosis knowledge base |
| POST | `/api/diagnosis/match` | Match symptoms against database |
| GET | `/api/diagnosis/patient/{id}` | Get patient diagnoses |
| POST | `/api/diagnosis` | Create diagnosis record |

### Discharge
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/discharge` | List discharge reports |
| GET | `/api/discharge/{id}` | Get discharge report |
| POST | `/api/discharge` | Create discharge report |
| POST | `/api/discharge/{id}/generate-pdf` | Generate PDF |
| GET | `/api/discharge/{id}/download` | Download PDF |

### Access Logs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/logs` | List/search logs (admin only) |

## 🧪 Testing

```bash
cd backend
python3 -m app.tests
```

The test suite covers:
- ✅ Password hashing with bcrypt
- ✅ JWT token creation and validation
- ✅ Expired token rejection
- ✅ User CRUD and unique constraints
- ✅ Patient CRUD and unique patient ID
- ✅ Medical report creation
- ✅ Diagnosis database seeding
- ✅ Discharge report creation
- ✅ Access log creation

## 🔐 Security Features

- **JWT Authentication** with configurable expiration
- **bcrypt** password hashing (industry standard)
- **Role-Based Access Control** with hierarchical permissions
- **Input Validation** via Pydantic schemas
- **SQL Injection Prevention** through SQLAlchemy ORM
- **XSS Protection** headers
- **Clickjacking Protection** (X-Frame-Options: DENY)
- **HSTS** headers for HTTPS enforcement
- **Cache Control** headers to prevent sensitive data caching
- **Comprehensive Audit Logging** of all system actions
- **Account Lockout** after failed login attempts

## 🗄️ Database Configuration

For **SQLite** (development, default):
```
DATABASE_URL=sqlite:///./hospital.db
```

For **MySQL** (production):
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hospital_db
```

## 🤖 AI Integration

The system supports AI-assisted medical report summarization. Configure your AI provider in `.env`:

```env
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_API_KEY=your-api-key
AI_MODEL=gpt-3.5-turbo
```

When no AI API is configured, the system falls back to intelligent mock analysis.

> **⚠️ Disclaimer**: The AI assistance is for reference only. Final medical decisions remain the responsibility of the attending physician.

## 📄 PDF Generation

Discharge PDFs are generated using ReportLab with:
- Professional hospital header
- Patient demographics
- Doctor information
- Clinical diagnosis and treatment
- Prescribed medications
- Follow-up instructions
- AI summary integration
- Digital signature section

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./hospital.db` |
| `JWT_SECRET_KEY` | JWT signing secret | Auto-generated |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `60` |
| `AI_API_KEY` | AI provider API key | `` (mock fallback) |
| `PDF_OUTPUT_DIR` | PDF storage directory | `./generated_pdfs` |

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── models/          # 8 SQLAlchemy models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── routers/         # 7 API route modules
│   │   ├── services/        # Business logic
│   │   ├── middleware/      # Auth + security middleware
│   │   └── utils/           # JWT, password utilities
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── pages/               # 10 HTML pages
│   ├── css/                 # 3 CSS files
│   └── js/                  # 10 JavaScript modules
└── start.sh                 # Start script
```

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3, FastAPI, SQLAlchemy, Uvicorn |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Database** | SQLite (dev) / MySQL (prod) |
| **Auth** | JWT, bcrypt |
| **PDF** | ReportLab |
| **AI** | OpenAI API / Mock fallback |

## 📜 License

[MIT License](LICENSE) - Copyright (c) 2026

---

Built with ❤️ for modern healthcare infrastructure.
