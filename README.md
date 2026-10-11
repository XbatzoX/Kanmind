# KanMind Backend 🧠

Welcome to the backend API of **KanMind**, a robust and secure Kanban board management application built with **Django** and **Django REST Framework (DRF)**.

This API handles multi-user collaboration, workspace permissions, task workflows, and real-time comment tracking with strict validation layers (PEP 8 & DRY compliant).

---

## 🛠️ Tech Stack & Features

- **Framework:** Django 5.x & Django REST Framework (DRF)
- **Authentication:** Token-based Authentication
- **Database:** SQLite (Local Development)
- **Key Features:**
  - Strict workspace boundaries (Only board owners/members can view or edit data).
  - Advanced input validation preventing unexpected payload attributes (HTTP 400 validation).
  - Optimized payload delivery (Compact task lists in nested endpoints).

---

## 💻 Installation & Setup

Follow these steps to clone and run this project locally on your machine.

### 1. Clone the Repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL_HERE>
cd <YOUR_PROJECT_FOLDER_NAME>
```

### 2. Setup the Virtual Environment
```bash
# Create environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Activate environment (Mac/Linux)
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Create Superuser
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start the Server
```bash
python manage.py runserver
```
The API will be accessible at `http://127.0.0`.

---

## 🚀 Testing the API with Postman

A fully automated test suite is included directly within this repository to verify all happy and unhappy paths (e.g., HTTP 200, 400, 403, and 404 boundaries).

### How to use it:
1. Navigate to the `/postman` directory in this project.
2. Import both `kanmind_collection.json` and `kanmind_environment.json` into your **Postman** application.
3. Select the `KanmindEnv` environment in the top-right corner of Postman.
4. Run the **Registration** or **Login** request first. The test scripts will automatically capture your `user_token` and apply it to all subsequent requests.
