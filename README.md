# 🎓 College Management System (CMS)

> **Phase 1 — Foundation & Core Architecture**

A modular, scalable, and Django-powered **College Management System (CMS)** designed to streamline academic administration, user management, and campus workflows.

The project is being developed incrementally across multiple phases. **Phase 1 focuses on establishing the core architecture, authentication system, database foundation, and modular application structure** required for future academic and campus-management features.

---

## 🌐 Live Demo

🚀 **Live Deployment:** [college-portal-pi.vercel.app](https://college-portal-pi.vercel.app)

The application is deployed on **Vercel** and uses **Neon PostgreSQL** for the production database.

---

## 📌 Project Status

> 🟢 **Phase 1 — Foundation Completed / Active Development**

Phase 1 establishes the technical backbone of the College Management System, including:

* Custom authentication
* Role-based access control
* Modular Django applications
* Academic database foundation
* Shared templates and configuration
* Development and production deployment setup

Future phases will progressively introduce academic management, attendance, analytics, AI-assisted functionality, notifications, and digital certification.

---

# ✨ Key Features

## 🔐 Custom Authentication

* Custom Django user model
* User registration and authentication
* Extensible user-role architecture
* Separate student and faculty profiles

## 👥 Role-Based Access Control

The system currently supports three primary roles:

| Role                    | Description                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| 👨‍💼 **Administrator** | System configuration, user management, and academic administration       |
| 👨‍🏫 **Faculty**       | Academic records, student evaluation, attendance, and subject management |
| 👨‍🎓 **Student**       | Personal academic information, attendance, marks, grades, and analytics  |

> Some role-specific functionality is planned for future development phases.

## 🏗️ Modular Architecture

The project follows a modular Django application structure:

* `accounts` — Authentication and user management
* `faculty` — Faculty-related functionality
* `students` — Student-related functionality
* `collegePortal` — Core Django project configuration
* `templates` — Shared user interface templates

## 🗄️ Database Foundation

The initial database architecture is designed to support:

* Departments
* Courses
* Subjects
* Student profiles
* Faculty profiles
* Academic relationships
* Initial grade-related structures

## ⚙️ Production-Ready Configuration

* Environment-based configuration
* SQLite support for local development
* PostgreSQL support for production
* Vercel deployment support
* Static file handling with WhiteNoise
* Database migrations
* Profile image upload support

---

# 🛠️ Technology Stack

## Backend

* **Python 3.11+**
* **Django 5.x**

## Database

* **SQLite3** — Local development
* **PostgreSQL** — Production
* **Neon** — Managed PostgreSQL hosting

## Frontend

* Django Templates
* HTML5
* CSS3
* JavaScript
* Tailwind CSS / Bootstrap 5

## Deployment

* **Vercel** — Python runtime and CDN delivery
* **Neon** — Production PostgreSQL database
* **WhiteNoise** — Static file management

## Planned Integrations

* Chart.js — Analytics and visualization
* Ollama — Local AI/LLM integration
* QR technologies — Attendance and certificate verification

---

# 📁 Project Structure

```text
collegePortal/
│
├── accounts/                 # Authentication and user management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── ...
│
├── faculty/                  # Faculty-related functionality
│   ├── models.py
│   ├── views.py
│   └── ...
│
├── students/                 # Student-related functionality
│   ├── models.py
│   ├── views.py
│   └── ...
│
├── collegePortal/            # Core project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── templates/                # Shared UI templates
│   ├── base.html
│   └── ...
│
├── manage.py
├── requirements.txt
└── README.md
```

> The project structure will evolve as additional modules are introduced in future phases.

---

# 🚀 Development Roadmap

The College Management System is planned as a multi-phase platform.

## 🧱 Phase 1 — Foundation

**Current Phase**

* Django project architecture
* Custom authentication
* Role-based access control
* Core database models
* Modular application structure
* Shared templates
* Development and deployment configuration

---

## 📚 Phase 2 — Academic Management

Planned features:

* Course and subject management
* Student academic profiles
* Faculty management
* Internal assessment management
* Marks and grade management
* Semester and academic organization
* Department and batch management

---

## 📱 Phase 3 — Attendance & Campus Workflows

Planned features:

* Dynamic QR-based attendance
* Time-limited attendance sessions
* Student QR check-in
* Attendance analytics
* Attendance threshold notifications
* Attendance history

---

## 📊 Phase 4 — Analytics & Intelligence

Planned features:

* Interactive academic dashboards
* GPA and grade analytics
* Attendance trend analysis
* Student performance rankings
* AI-assisted academic analysis
* Automated merit and poster generation
* Local LLM integration using Ollama

---

## 🏅 Phase 5 — Digital Certification

Planned features:

* Digital merit badges
* Certificate generation
* QR-based certificate verification
* Public certificate verification pages
* Tamper-resistant verification workflows

---

# 🏛️ System Architecture

The long-term system architecture is designed to evolve into a modular platform:

```text
                    ┌─────────────────────┐
                    │       Users         │
                    │ Admin / Faculty /   │
                    │       Student       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Django Backend    │
                    │ Authentication/RBAC │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
    ┌───────────┐        ┌───────────┐        ┌───────────┐
    │ Students  │        │  Faculty  │        │ Academic  │
    │   Module  │        │   Module  │        │  Module   │
    └───────────┘        └───────────┘        └───────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │      Database       │
                    │ SQLite / PostgreSQL │
                    └─────────────────────┘
```

Future modules such as attendance, analytics, AI services, notifications, and digital certification can be integrated without restructuring the core system.

---

# 🗄️ Database Architecture

The database architecture is designed to support a **KTU-style academic workflow** and can be expanded incrementally as the project evolves.

```text
User
 │
 ├── Student Profile
 │
 └── Faculty Profile
       │
       └── Department
             │
             ├── Course
             │
             └── Subject
                    │
                    └── Academic Records
```

---

# 📊 Development Status

| Component             | Status         |
| --------------------- | -------------- |
| Project Setup         | ✅ Completed    |
| Django Configuration  | ✅ Completed    |
| Custom Authentication | ✅ Completed    |
| User Roles            | ✅ Completed    |
| Accounts App          | ✅ Completed    |
| Faculty App           | ✅ Initialized  |
| Students App          | ✅ Initialized  |
| Database Foundation   | ✅ Initialized  |
| Academic Workflow     | 🔄 In Progress |
| Attendance System     | ⏳ Planned      |
| Analytics             | ⏳ Planned      |
| AI Integration        | ⏳ Planned      |
| Digital Certificates  | ⏳ Planned      |

### Legend

* ✅ Completed
* 🔄 In Progress
* ⏳ Planned

---

# ⚙️ Local Development Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/unni24061-ux/collegePortal.git
cd collegePortal
```

Development fork:

```text
https://github.com/zamanv/collegePortal.git
```

---

## 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
```

---

## 3️⃣ Activate the Virtual Environment

### Windows — PowerShell

```powershell
venv\Scripts\Activate.ps1
```

### Windows — Command Prompt

```cmd
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

The project currently uses a minimal dependency set including:

* Django
* WhiteNoise
* psycopg2-binary
* python-dotenv
* Pillow

---

## 5️⃣ Configure Environment Variables

Create a `.env` file in the project root if you want to override the default configuration.

```dotenv
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### Database Behaviour

* Without `DATABASE_URL` → SQLite is used for local development.
* With `DATABASE_URL` → PostgreSQL is used.

---

## 6️⃣ Apply Database Migrations

```bash
python manage.py migrate
```

---

## 7️⃣ Create an Administrator Account

```bash
python manage.py createsuperuser
```

Follow the terminal prompts to configure the administrator account.

---

## 8️⃣ Start the Development Server

```bash
python manage.py runserver
```

The application will normally be available at:

```text
http://127.0.0.1:8000/
```

---

# 🚀 Deployment

The project is configured for deployment using the **Vercel Python runtime**.

The Django application is detected through `manage.py`, with:

```text
collegePortal.wsgi.application
```

used as the WSGI entry point.

## Required Environment Variables

| Variable        |   Required  | Description                   |
| --------------- | :---------: | ----------------------------- |
| `DATABASE_URL`  |      ✅      | PostgreSQL connection string  |
| `SECRET_KEY`    | Recommended | Django secret key             |
| `DEBUG`         |   Optional  | Set to `False` in production  |
| `ALLOWED_HOSTS` |   Optional  | Comma-separated allowed hosts |

## Deploy to Production

```bash
vercel login
vercel deploy --prod
```

Static files are collected during deployment and served through the Vercel CDN.

### Production Database Migration

From your local machine:

```powershell
$env:DATABASE_URL = "postgresql://user:password@host:port/dbname"
python manage.py migrate
```

> **Note:** User-uploaded files stored locally do not persist on Vercel's serverless environment. A cloud storage provider should be integrated when persistent uploads are required.

---

# 🔐 User Roles

## 👨‍💼 Administrator

Responsible for:

* User management
* Academic configuration
* Department and course management
* System administration

## 👨‍🏫 Faculty

Designed to support:

* Subject management
* Student evaluation
* Attendance
* Academic records
* Performance monitoring

## 👨‍🎓 Student

Designed to provide access to:

* Personal academic information
* Courses and subjects
* Attendance records
* Marks and grades
* Performance analytics

---

# 🤝 Contributors

### Development Team

* **Unnikrishnan UR**
* **Adil Zaman V**

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

```bash
# Fork the repository
git fork

# Clone your fork
git clone <your-fork>

# Create a feature branch
git checkout -b feature/your-feature
```

After making your changes:

1. Test the application locally.
2. Commit your changes.
3. Push the feature branch.
4. Submit a Pull Request.

---

# 📜 License

License information will be added as the project progresses.

---

<div align="center">

### 🚧 Built incrementally — one phase at a time.

**College Management System (CMS)**

⭐ If you find this project useful, consider giving the repository a star!

</div>
