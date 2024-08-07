# Quiz Application

This project is a quiz application built using Flask. It allows users to register, log in, and take quizzes. Admins can review questions, add comments, and view student progress.

## Features

- User Authentication (Register, Login, Logout)
- Role-Based Access (Admin and Student)
- Quiz Management
  - Admin can add quiz questions
  - Students can take quizzes and view feedback
- Progress Tracking
  - Students can see their progress and scores
  - Admins can view students' progress

## Setup

### Prerequisites

- Python 3.x
- Virtual Environment (venv)

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Isma3l-19/quiz_app
    cd quiz_app
    ```

2. **Create and activate a virtual environment:**
    - On Windows:
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    - On Windows:
      ```bash
      set FLASK_APP=run.py
      set FLASK_ENV=development
      ```
    - On macOS/Linux:
      ```bash
      export FLASK_APP=run.py
      export FLASK_ENV=development
      ```

5. **Initialize and apply database migrations:**
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

6. **Run the application:**
    ```bash
    flask run
    ```

The application will be accessible at `http://127.0.0.1:5000`.

## Usage

### Registering a User

1. Navigate to the registration page (`/register`).
2. Fill in the registration form and submit.

### Logging In

1. Navigate to the login page (`/login`).
2. Enter your credentials and log in.

### Admin Actions

- **Add Questions:**
  Navigate to the admin page and add quiz questions.

- **Review Questions:**
  View and add comments to quiz questions which students can see as feedback.

- **View Student Progress:**
  Track the progress and scores of students.

### Student Actions

- **Take Quizzes:**
  Select a topic and start taking quizzes. After each question, the next question will load automatically.

- **View Feedback:**
  After a question is reviewed by the admin, view feedback for each question.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
