# Mini Jira

Mini Jira is a project management tool built using Django and Django Rest Framework (DRF). It aims to provide task and project management features with collaboration capabilities such as task discussions, comments, and real-time updates.

## Setup & Run Instructions

### Prerequisites

Ensure you have the following installed:
- Python 3.8 or above
- pip (Python package installer)
- Virtual environment tool (optional but recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/your_username/mini-jira.git
cd mini-jira
```

### 2. Create and Activate a Virtual Environment (optional but recommended)

# For Linux/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate


### 3. Install Dependencies

pip install -r requirements.txt

### 4. Apply Database Migrations
python manage.py migrate

### 5. Create a Superuser (optional)
python manage.py createsuperuser

### 6. Run the Development Server
python manage.py runserver


# Design/Architecture Choices
mini_jira/
├── apps/                     # All Django apps are in this folder
│   ├── accounts/             # User authentication and registration
│   ├── collaborations/       # Project invitations and collaboration management
│   ├── tasks/                # Task management, including comments and discussions
│   ├── projects/             # Project-related data models and views
│   └── registration/         # User registration APIs
├── mini_jira/                # Core project settings, including ASGI, WSGI, and constants
├── manage.py                 # Django management command utility
├── requirements.txt          # List of dependencies
├── pytest.ini                # Pytest configuration for test discovery
└── db.sqlite3                # Database file (use PostgreSQL for production)

## Key Design Choices
- Django Apps: The project is divided into individual apps for specific modules like tasks, projects, collaborations, etc. This promotes modularity and easier maintainability.
- Real-Time Features: WebSockets and Django Channels are used to implement real-time task updates, discussions, and comments.
- Permissions: Custom permissions like ProjectCollaboratorPermission and TaskCollaboratorPermission are used to control access to various endpoints based on user roles and project membership.
- UUIDs: UUIDs are used as primary keys for various models (e.g., Task, Project) to provide better security and avoid ID collisions, especially in larger systems.
- Task Management: Tasks can have comments, discussions, and multiple states, and these features are tightly integrated into the workflow to allow for smooth collaboration between users.
- Signal Integration: Django signals are used for event-based tasks like sending notifications when a comment is added or when a task is updated.
- WebSockets: WebSockets (via Django Channels) are used for real-time task and comment updates. The application listens to - WebSocket channels and notifies users of updates to tasks, comments, and discussions.


## How to Run Tests

pip install pytest
pytest
pytest apps/tasks/tests.py

