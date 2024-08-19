# Quiz Application

This project is a dynamic quiz application built using Flask. It allows users to register, log in, and take quizzes. The application supports role-based access control, enabling admins to manage quiz content and monitor student progress, while students can take quizzes, track their scores, and receive feedback.

## Features

- **User Authentication:**
  - Register, Login, and Logout functionalities.
  - Secure password storage using hashing.
  
- **Role-Based Access:**
  - Admin and Student roles with distinct dashboards.
  
- **Quiz Management:**
  - Admins can create quiz sets, add questions, and manage quizzes.
  - Students can take quizzes, view their scores, and receive feedback.

- **Progress Tracking:**
  - Students can monitor their progress, view scores, and track their performance over time.
  - Admins can view and review the progress of all students.

- **Feedback System:**
  - Admins can provide feedback on quiz performance.
  - Students can view feedback from admins.

- **REST API:**
  - Exposes quiz management endpoints for creating and retrieving quiz questions via a REST API.

- **Dark/Light Mode:**
  - Toggle between dark and light themes for a better user experience.

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
2. Fill in the registration form with a username, email, password, and role (Student or Admin).
3. Submit the form to create an account.

### Logging In

1. Navigate to the login page (`/login`).
2. Enter your email and password.
3. Upon successful login, you will be redirected to the appropriate dashboard based on your role.

### Admin Actions

- **Add Quiz Sets and Questions:**
  - Admins can create new quiz sets and add questions to them through the admin dashboard.

- **Review Student Progress:**
  - View a list of all students and their quiz performance, including the number of completed quizzes and scores.

- **Provide Feedback:**
  - Admins can add comments and feedback on student performance in specific quizzes.

### Student Actions

- **Take Quizzes:**
  - Students can select a quiz set from their dashboard and start taking quizzes. Questions are displayed one at a time.

- **View Scores and Feedback:**
  - After completing quizzes, students can view their scores and feedback provided by the admin.


## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your improvements or bug fixes. Ensure your code follows the existing coding conventions and is well-documented.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
