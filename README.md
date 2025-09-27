# ALX Project Nexus – Job Board Backend

[![CI](https://github.com/ochogwuprince92/alx-project-nexus/actions/workflows/ci.yml/badge.svg)](https://github.com/ochogwuprince92/alx-project-nexus/actions/workflows/ci.yml)
[![Docker Publish CI](https://github.com/ochogwuprince92/alx-project-nexus/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/ochogwuprince92/alx-project-nexus/actions/workflows/docker-publish.yml)

## Repository URL
[GitHub Repo – alx-project-nexus](https://github.com/ochogwuprince92/alx-project-nexus)

---

## Project Objective
The goal of **Project Nexus (ProDev BE Capstone)** is to design and implement a **backend for a Job Board Platform**.  
This project demonstrates the ability to build **scalable, secure, and production-ready backend systems** with modern engineering practices.

---

## Overview
This case study focuses on developing a **Job Board Backend** that enables:  
- **Job postings & applications**  
- **Role-based access control (RBAC)**  
- **Efficient job search with caching and indexing**  
- **Background processing for notifications**  
- **Comprehensive API documentation**  

The system follows **best practices** in API development, security, database optimization, and deployment automation.

---

## Project Goals
1. **API Development** – Build RESTful APIs for managing job postings, categories, and applications.  
2. **Access Control** – Implement **JWT-based authentication** with **phone or email login** and role permissions.  
3. **Database Optimization** – Ensure fast job searches with indexing and query optimization.  
4. **Caching** – Use Redis to improve performance for frequent queries.  
5. **Background Tasks** – Offload notifications and reports with RabbitMQ + Celery.  
6. **CI/CD & Deployment** – Automate testing, containerization, and deployment with GitHub Actions, Docker, and Kubernetes.  

---

## Technologies Used
| Technology       | Purpose |
|------------------|---------|
| **Django + DRF** | Backend framework and REST API development |
| **PostgreSQL**   | Relational database for jobs, users, and applications |
| **JWT**          | Authentication using phone/email login |
| **Redis**        | Caching for search queries & token management |
| **RabbitMQ + Celery** | Background task processing (emails, notifications) |
| **Swagger/OpenAPI** | API documentation |
| **Docker**       | Containerization for consistent deployments |
| **Kubernetes**   | Orchestration and scaling |
| **GitHub Actions** | CI/CD automation pipeline |

---

## Quickstart (Local)

1. Create and activate a virtual environment (optional: use the provided `yob/` venv on this repo):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy environment template and set values:

   ```bash
   cp .env.example .env  # if available; otherwise create .env based on settings
   ```

   Required settings (examples):

   - `DJANGO_TESTING=1` (to force SQLite during local dev)
   - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`

3. Run migrations and start server:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

4. Open API docs:

   - Swagger UI: `http://127.0.0.1:8000/swagger/`
   - Redoc: `http://127.0.0.1:8000/redoc/`

---

## Quickstart (Docker)

1. Ensure your `.env` file is present locally (not committed). The Docker build ignores `.env` via `.dockerignore`.

2. Build the image:

   ```bash
   docker build -t ghcr.io/ochogwuprince92/alx-project-nexus:local .
   ```

3. Run with your `.env` file:

   ```bash
   docker run --rm -p 8000:8000 --env-file .env ghcr.io/ochogwuprince92/alx-project-nexus:local
   ```

4. Open Swagger: `http://127.0.0.1:8000/swagger/`

---

## Key Features
- **Job Posting Management**  
  - CRUD APIs for jobs and categories.  
  - Categorization by industry, type, and location.  

- **Role-Based Authentication**  
  - **Admin**: manage jobs, categories, and users.  
  - **Job Seeker**: search/apply for jobs, manage applications.  
  - Authentication via **phone or email (one at a time)**.  

- **Optimized Job Search**  
  - Full-text search and filtering.  
  - PostgreSQL indexing (GIN/B-Tree).  
  - Redis caching for repeated queries.  

- **Background Tasks**  
  - Celery + RabbitMQ for async processing.  
  - Email/SMS notifications after applications.  


- **Feature Development**  
  - `feat: implement job posting and filtering APIs`  
  - `feat: add role-based authentication for admins and users`  

- **Optimization & Scalability**  
  - `perf: optimize job search with indexing and Redis caching`  
  - `chore: integrate Celery with RabbitMQ for background tasks`  

- **Documentation**  
  - `feat: integrate Swagger for API documentation`  
  - `docs: update README with usage details`  

- **CI/CD & Deployment**  
  - `chore: add GitHub Actions workflow for testing and deployment`  
  - `chore: configure Kubernetes manifests for production`  

---

## Submission Details
- **Deployment**: API + Swagger docs will be hosted and accessible online.  
- **Evaluation Criteria**:
  - Job & category CRUD APIs function correctly.  
  - Role-based authentication works with phone/email login.  
  - Queries are indexed and optimized.  
  - Redis caching improves performance.  
  - Celery + RabbitMQ handle background tasks.  
  - CI/CD pipeline automates build/test/deploy.  
  - Documentation is complete and hosted.  

---

## Conclusion
The **Nexus Job Board Backend** demonstrates backend engineering skills by combining:  
- Clean API design  
- Secure authentication  
- Optimized queries & caching  
- Background task management  
- Automated CI/CD and containerized deployment  

This project is **production-ready** and reflects **industry-standard backend engineering practices**.

---

## Author
**Prince Ochogwu**  
- GitHub: [ochogwuprince92](https://github.com/ochogwuprince92)  
- LinkedIn: [ochogwuprince](https://linkedin.com/in/your-link)  
- Email: ochogwuprince92@gmail.com  
