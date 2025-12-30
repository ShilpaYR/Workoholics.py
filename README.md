# Intelligent HR Recruitment Portal with RAG-Based Chatbot

## Abstract

The **Intelligent HR Recruitment Portal with RAG-Based Chatbot** is a secure, multi-role web application designed to modernize enterprise HR operations and recruitment workflows. The platform unifies **Employees**, **HR staff**, and **Job Applicants** into a single system that supports internal HR policy assistance, job posting management, and intelligent candidate screening.

The system integrates a **Retrieval-Augmented Generation (RAG)** chatbot that answers employee HR and policy-related questions using organization-specific documents, ensuring responses are grounded in real data and minimizing hallucinations. In addition, the portal includes **agentic pipelines** for resume validation, enrichment, deduplication, and routing to assist HR teams in efficiently handling large volumes of applications.

The backend is implemented using **Flask-based microservices**, while the frontend is built as a **Vue.js single-page application (SPA)**. The platform supports **role-based access control**, **TOTP-based two-factor authentication (2FA)** for employees, and **Google SSO** for applicants. Vector-based semantic search (ChromaDB) and large language models are used to enable intelligent HR policy Q&A and automated resume analysis.

---

## System Overview

### User Roles
- **Employee** – Secure login with email/password + TOTP, HR policy chatbot access  
- **HR** – Job posting management and AI-assisted applicant filtering  
- **Applicant** – Google SSO login, job browsing, and guided application submission  

### Core Features
- RAG-based HR policy chatbot  
- Agentic resume screening pipeline  
- Secure authentication (JWT, TOTP, Google OAuth)  
- Microservice-based backend  
- Vue.js SPA frontend  

---

## Tech Stack

### Backend
- Python 3.x  
- Flask (microservices)  
- ChromaDB (vector database)  
- SQLite / PostgreSQL  
- JWT Authentication  
- Google OAuth 2.0  

### Frontend
- Vue.js  
- Vue Router  
- Axios  

### AI & Security
- Google `text-embedding-004`  
- Gemini LLM (e.g., Gemini 2.5 Flash)  
- Google Authenticator (TOTP)  

---

## Repository Structure

```
Workoholics-Project/
│
├── Backend/
│   ├── auth_service/
│   ├── rag_service/
│   ├── hr_service/
│   ├── applicant_service/
│   ├── requirements.txt
│   └── .env.example
│
├── Frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md
```

---

## How to Run the Project Locally

### Prerequisites

- Python 3.9+  
- Node.js 18+  
- npm  
- Git  
- Google Cloud credentials (LLM & Embeddings, OAuth)

---

### Clone the Repository

```bash
git clone https://github.com/ShilpaYR/Workoholics-Project.git
cd Workoholics-Project
```

---

### Backend Setup

```bash
cd Backend
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Create a `.env` file in `Backend/`:

```env
GOOGLE_API_KEY=your_google_llm_api_key
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_secret
JWT_SECRET=your_jwt_secret
DATABASE_URL=sqlite:///hr_portal.db
```

---

### Start Backend Services

```bash
python auth_service/app.py
python rag_service/app.py
python hr_service/app.py
python applicant_service/app.py
```

---

### RAG Document Ingestion

```bash
python rag_service/ingest.py --docs ./data/hr_policies/
```

---

### Frontend Setup

```bash
cd ../Frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## Authentication

- Employees: Email/password + TOTP  
- Applicants: Google SSO  
- HR: Role-based access  

---

## Example Flows

- Employee → HR chatbot  
- HR → Job creation & applicant review  
- Applicant → Google login → Job application  

---

## Future Enhancements

- Candidate scoring & ranking  
- HR analytics dashboards  
- Multi-language support  
- External ATS integrations  

---

## Authors

- Shilpa Yelkur Ramakrishnaiah
- Abhishek Darji  
- Aniket Anil Naik  
