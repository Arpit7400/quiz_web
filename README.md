
# Quiz API

This is a Flask-based API for managing quizzes, users, and quiz-related data. It allows users to create quizzes, manage subjects, topics, and subtopics, and retrieve quizzes based on various filter criteria.

## Table of Contents

- [Setup](#setup)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [License](#license)

## Setup

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/Arpit7400/quiz_web.git
   ```

2. Install the required dependencies using pip:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you have a MongoDB server running, and update the MongoDB connection string in the `app.config['MONGO_URI']` variable within `app.py` to point to your MongoDB instance.

4. Start the Flask application:

   ```bash
   python app.py
   ```

The API should now be running locally on `http://localhost:5000`.

## API Endpoints

### Authentication

- **POST /login**
  - Log in a user by providing an email, password, and role (e.g., "user" or "admin").

### Users

- **POST /user**
  - Create a new user by providing a name, email, and password.

- **GET /user**
  - Get a list of all users.

- **GET /user/{user_id}**
  - Get details of a specific user by user ID.

- **PUT /user/{user_id}**
  - Update user information, such as name, email, or password.

- **PUT /block/user/{user_id}**
  - Block or unblock a user.

### Subjects, Topics, and Subtopics

- **POST /create_language**
  - Create a new language.

- **GET /get_all_subject_quizz**
  - Get a list of all subjects for quizzes.

- **GET /get_subject_topics/{subject}**
  - Get topics for a specific subject.

- **GET /get_subject_subtopics/{subject}/{topic}**
  - Get subtopics for a specific subject and topic.

- **POST /add_Subject_quizz**
  - Add subjects, topics, or subtopics. Also, you can add images for subjects, topics, and subtopics.

### Quizzes

- **GET /get_all_quizz**
  - Get a list of all quizzes.

- **GET /get_quizz/{quiz_id}**
  - Get details of a specific quiz by quiz ID.

- **POST /create_quiz/{creator_id}**
  - Create a new quiz by providing various details such as language, class, subject, topic, subtopic, level, quiz type, questions, and options.

- **PUT /update_quizz/{quiz_id}/{creator_id}**
  - Update an existing quiz by quiz ID and creator ID. You can update quiz details, questions, and options.

- **DELETE /delete_quizz/{quiz_id}/{creator_id}**
  - Delete a quiz. (This is not a real deletion but hides the quiz from everyone.)

### Filtering Quizzes

- **GET /get_quizzes_by_filter**
  - Get quizzes based on filter criteria. You can filter by subject, topic, subtopic, and level.

## Usage

- To create quizzes, you can use the `/create_quiz/{creator_id}` endpoint by providing the required details.
- You can manage users, subjects, topics, and subtopics using the respective endpoints.
- To retrieve quizzes based on specific criteria, use the `/get_quizzes_by_filter` endpoint by providing subject, topic, subtopic, and level as query parameters.

## License

This project is licensed under the [MIT License](LICENSE).
```

Make sure to replace `https://github.com/your-username/quiz-api.git` with the actual GitHub repository URL where you plan to host this code.

You can add this `README.md` file to your GitHub repository to provide documentation for your API.