from flask import Flask, request, jsonify, request
from flask_pymongo import PyMongo
from bson import ObjectId, json_util, Binary
from flask_cors import CORS
from werkzeug .security import generate_password_hash,check_password_hash
from bson import json_util
from bson.json_util import dumps

import os
import datetime


app = Flask(__name__)
CORS(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Quizes'
mongo_q = PyMongo(app)


# API's supporter functions
def get_entities(collection_name, dbinitialize):
    all_entities = list(dbinitialize.db[collection_name].find())
    return jsonify(all_entities)

def got_entities(collection_name, dbinitialize):
    all_entities = list(dbinitialize.db[collection_name].find())
    return (json_util.dumps(all_entities))


def get_filtered(collection_name, dbinitialize):
    all_entities = list(dbinitialize.db[collection_name].find())
    return (all_entities)

def get_entity(collection_name, entity_id, dbinitialize):
    entity = dbinitialize.db[collection_name].find_one({"_id": entity_id})
    return entity


def update_entity(collection_name, entity_id, entity_data):
    result = mongo_q.db[collection_name].update_one({"_id": entity_id},
                                                  {"$set": entity_data})
    if result.modified_count == 0:
        return jsonify({"error": f"{collection_name.capitalize()} notfound"}), 404
    updated_entity = mongo_q.db[collection_name].find_one({"_id": entity_id})
    return jsonify(updated_entity)


def delete_entity(collection_name, entity_id):
    deleted_entity = mongo_q.db[collection_name].find_one_and_delete({"_id": entity_id})
    if deleted_entity is None:
        return jsonify({"error": f"{collection_name.capitalize()} not found"}), 404
    return jsonify(deleted_entity)


def block_entity(collection_name, entity_id):
    entity = mongo_q.db[collection_name].find_one({"_id": entity_id})
    if not entity:
        return jsonify({"error": f"{collection_name.capitalize()} not found"}), 404

    new_blocked_value = not entity.get("blocked", False)  # Toggle the 'blocked' value
    result = mongo_q.db[collection_name].update_one({"_id": entity_id}, {"$set": {"blocked": new_blocked_value}})

    if result.modified_count == 0:
        return jsonify({"error": f"Failed to update {collection_name.capitalize()}'s 'blocked' status"}), 500

    updated_entity = mongo_q.db[collection_name].find_one({"_id": entity_id})

    return jsonify(updated_entity), 200

# ****************
# Login endpoint to authenticate users
@app.route('/login', methods=["POST"])
def login_user():
    if 'email' not in request.json or 'password' not in request.json or 'role' not in request.json:
        return jsonify({"message": "Missing email, password, or role in request"}), 400

    email = request.json['email']
    password = request.json['password']
    role = request.json['role']

    # Find the user by email
    user = mongo_q.db.users.find_one({"email": email, "role": role})
    print("-", user)
    if user and check_password_hash(user['password'], password):
        # User exists and credentials are valid
        # session['user_id'] = str(user['_id'])
        # session['role'] = role
        
        user['_id'] = str(user['_id'])
        if role == 'admin':
            return jsonify({"message": "admin", "user": user})

        return jsonify({"message": "user", "user": user})
    else:
        # Invalid credentials or user not found
        return jsonify({"message": "Invalid credentials"}), 401

# Create a new user
@app.route('/user', methods=['POST'])
def create_user():
    if 'name' not in request.json or 'password' not in request.json or 'email' not in request.json:
        return jsonify({"error": "Missing name or password in request"}), 400

    name = request.json['name']
    password = request.json['password']
    email = request.json['email']

    if len(password) < 8:
        return jsonify({"error": "Password too short"}), 400

    hashed_password = generate_password_hash(password, method='sha256')

    user_data = {
        "_id": str(ObjectId()),
        "name": name,
        "password": hashed_password,
        "email": email,
        "role": "user",
        "blocked": False
    }

    print(user_data)

    inserted_id = mongo_q.db.users.insert_one(user_data).inserted_id

    inserted_user = mongo_q.db.users.find_one({"_id": inserted_id})
    inserted_user["_id"] = str(inserted_user["_id"])
    print("Inserted user:", inserted_user)

    return jsonify(inserted_user)

# Get all users
@app.route('/user', methods=['GET'])
def get_users():
    entities = list(mongo_q.db.users.find({"role": "user"}))
    for user in entities:
        user['_id'] = str(user['_id'])
    return jsonify(entities)

# Get a single user by user ID
@app.route('/user/<string:user_id>', methods=['GET'])
def get_user(user_id):
    user_data = get_entity('users', user_id)  # Replace this with your actual code to retrieve the user data
    if user_data is None:
        # If user data is not found, you can return an error response
        return jsonify({"error": "User not found"}), 404

    # If user data is found, return a JSON response with the user data
    return jsonify(user_data), 200


# Update user information
@app.route('/user/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    user_data = {}
    if 'name' in request.json:
        user_data['name'] = request.json['name']
    if 'password' in request.json:
        password = request.json['password']
    if 'email' in request.json:
        user_data['email'] = request.json['email']
        if len(password) < 8:
            return jsonify({"error": "Password too short"}), 400
        hashed_password = generate_password_hash(password,
                                                 method='sha256')
        user_data['password'] = hashed_password

    return update_entity('users', user_id, user_data)

# Block or unblock a user
@app.route('/block/user/<string:user_id>', methods=['PUT'])
def block_user(user_id):
    return block_entity('users', user_id)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'} 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/upload_image', methods=['POST'])
def upload_image(image):
    if image and allowed_file(image.filename):
        image_data = Binary(image.read())
        image_id = mongo_q.db.images.insert_one({"image_data": image_data}).inserted_id
        filename = str(image_id)
        return filename
    else:
        return None
  
#for getting image from database
@app.route('/get_image/<image_id>', methods = ['GET'])
def get_image(image_id):
    try:
        image_data = mongo_q.db.images.find_one({"_id": ObjectId(image_id)})
        if image_data:
            response = app.response_class(image_data["image_data"], mimetype='image/jpeg')
            return response
        else:
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        return jsonify({"error": "Error fetching the image.", "details": str(e)}), 500


#create new languagae
@app.route('/create_language', methods=['POST'])
def create_language():
    try:
        language = request.form.get('language')
        inserted = mongo_q.db.languages.insert_one({'name': language})

        if inserted.inserted_id:
            return jsonify({"message": "Language created successfully.", "language": language}), 201
        else:
            return jsonify({"error": "Failed to create language."}), 500
    except Exception as e:
        return jsonify({"error": "An error occurred.", "details": str(e)}), 500



# Getting all subject 
@app.route('/get_all_subject_quizz', methods = ['GET'])
def get_all_subject_quizz():
    return got_entities('quizz_subjects', mongo_q)

# Getting topic of selected subject 
@app.route('/get_subject_topics/<string:subject>', methods = ['GET'])
def get_subject_topics(subject):
    All_topics = mongo_q.db.quizz_subjects.find_one({'subject':subject})
    topics = [i for i in All_topics['topics'] ]
    return (topics)

# Getting subtopics of selected subject and topic
@app.route('/get_subject_subtopics/<string:subject>/<string:topics>', methods = ['GET'])
def get_subject_subtopics(subject,topics):
    All_subtopics = mongo_q.db.quizz_subjects.find_one({'subject':subject})
    subtopics = All_subtopics['topics'][topics]
    return jsonify(subtopics)



# Create and update a route to add subjects, topics, or subtopics
@app.route('/add_Subject_quizz', methods=['POST'])
def add_Subject_quizz():
    try:  
        subject_name = request.form.get('subject')
        if not subject_name:
            return jsonify({"message": "Subject name is required."}), 400
        subject_image = request.files.get('subject_image')
        subject_image_filename = upload_image(subject_image)

        subject_document = mongo_q.db.quizz_subjects.find_one({'subject': subject_name})

        if subject_document is None:
            # Subject doesn't exist in the database, create it
            subject_document = {'subject': subject_name, 'topics': {}, 'subject_image': subject_image_filename}
            mongo_q.db.quizz_subjects.insert_one(subject_document)

        topic_name = request.form.get('topic')
        subtopic_name = request.form.get('subtopic')
        
        if topic_name:
            if topic_name not in subject_document['topics']:
                # Check if an image file is included in the request for the topic
                topic_image = request.files.get('topic_image')
                topic_image_filename = upload_image(topic_image)

                subject_document['topics'][topic_name] = {'subtopics': {}, 'topic_image': topic_image_filename}
                mongo_q.db.quizz_subjects.update_one({'subject': subject_name}, {'$set': {'topics': subject_document['topics']}})

        if subtopic_name:
            if not topic_name:
                return jsonify({"message": "Cannot add subtopic without a topic."}), 400

            if topic_name not in subject_document['topics']:
                return jsonify({"message": "Topic does not exist in the subject."}), 400

            # Check if an image file is included in the request for the subtopic
            subtopic_image = request.files.get('subtopic_image')
            subtopic_image_filename = upload_image(subtopic_image)

            if subtopic_name not in subject_document['topics'][topic_name]['subtopics']:
                subject_document['topics'][topic_name]['subtopics'][subtopic_name] = {'subtopic_image': subtopic_image_filename}
                mongo_q.db.quizz_subjects.update_one({'subject': subject_name}, {'$set': {'topics': subject_document['topics']}})

        return jsonify({"message": "Data added successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get all quizes
@app.route('/get_all_quizz', methods = ['GET'])
def get_all_quizz():
    return get_entities('quizes', mongo_q)

# Get single quiz using its id
@app.route('/get_quizz/<string:quiz_id>', methods = ['GET'])
def get_quizz(quiz_id):
    return get_entity('quizes', quiz_id, mongo_q)



# Create new Quiz requires creator user id
@app.route('/create_quiz/<string:creator_id>', methods=[ 'POST'])
def create_quiz(creator_id):
    try:
        language = request.form.get('language')
        class_name = request.form.get('class')
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        subtopic = request.form.get('subtopic')
        level = request.form.get('level')
        quiz_type = request.form.get('quiz_type')
        # Get question container data
        question = request.form.get('question')
        question_image = request.files.get('question_image')
        question_image_url = None

        if question_image and allowed_file(question_image.filename):
            try:
                # filename = ''
                image_data = Binary(question_image.read())
                image_id = mongo_q.db.images.insert_one({"image_data": image_data}).inserted_id
                question_image_url = str(image_id)
            except Exception as e:
                return jsonify({"message": "Error uploading question image.", "error": str(e)}), 500
        
        options = []
        i = 1
        while True:
            option_text = request.form.get(f'option_{i}')
            option_image = request.files.get(f'option_{i}_image')
            option_image_url = None
            if not option_text:  # If option_text is empty, exit the loop
                break
            
            if option_image and allowed_file(option_image.filename):
                try:
                    # Save the option image to the 'uploads' folder
                    image_data = Binary(question_image.read())
                    image_id = mongo_q.db.images.insert_one({"image_data": image_data}).inserted_id
                    option_image_url = str(image_id) # Store the file path in the database

                except Exception as e:
                    return jsonify({"message": f"Error uploading option {i} image.", "error": str(e)}), 500
                
            option_data = {
                'text': option_text,
                'image_url': option_image_url,
                'is_answer': request.form.get(f'is_answer_{i}') == 'true'
            }

            options.append(option_data)

            i += 1  # Increment the option counter


        new_quiz = {
            "_id": str(ObjectId()),
            "creator_id": creator_id,
            "quizz_add_time": datetime.datetime.now(),
            "language": language,
            "class": class_name,
            "subject": subject,
            "topic": topic,
            "subtopic": subtopic,
            "level": level,
            "quiz_type": quiz_type,
            'question_container': {
            'question': question,
            'question_image_url': question_image_url,
            'options': options
            },
            "blocked": False   # if it is False, then show to all, if True then hide from everybody also from creator
        }

        inserted_result = mongo_q.db.quizes.insert_one(new_quiz)
        inserted_id = inserted_result.inserted_id
        inserted = mongo_q.db.quizes.find_one({"_id": inserted_id})
        response_data = {"message": "Quiz created successfully", "_id": str(inserted["_id"])}
        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500
    


# Update quiz requires quiz id and creator id
@app.route('/update_quizz/<string:quiz_id>/<string:creator_id>', methods=['PUT'])
def update_quizz(quiz_id, creator_id):
    try:
        quiz = mongo_q.db.quizes.find_one({"_id": quiz_id})

        if quiz:
            if quiz["creator_id"] != creator_id:
                return jsonify({"message": "Unauthorized access. You do not have permission to update this quiz."}), 403

            # Get the updated quiz data from the request
            updated_data = request.form  # Assuming JSON data is sent in the request

            # Update language, class, subject, topic, subtopic, level, and quiz_type if provided
            if 'language' in updated_data:
                quiz["language"] = updated_data['language']
            if 'class' in updated_data:
                quiz["class"] = updated_data['class']
            if 'subject' in updated_data:
                quiz["subject"] = updated_data['subject']
            if 'topic' in updated_data:
                quiz["topic"] = updated_data['topic']
            if 'subtopic' in updated_data:
                quiz["subtopic"] = updated_data['subtopic']
            if 'level' in updated_data:
                quiz["level"] = updated_data['level']
            if 'quiz_type' in updated_data:
                quiz["quiz_type"] = updated_data['quiz_type']

            # Update question, question_image_url, and options if provided
            if 'question_container' in updated_data:
                question_container = updated_data['question_container']

                if 'question' in question_container:
                    quiz["question_container"]["question"] = question_container['question']

                if 'question_image_url' in question_container:
                    quiz["question_container"]["question_image_url"] = question_container['question_image_url']

                if 'options' in question_container:
                    options = []

                    for opt in question_container['options']:
                        # Here, we assume that 'text' and 'is_answer' are always present
                        option_data = {
                            'text': opt['text'],
                            'is_answer': opt['is_answer']
                        }

                        # Check if 'image_url' is provided
                        if 'image_url' in opt:
                            option_data['image_url'] = opt['image_url']

                        options.append(option_data)

                    quiz["question_container"]["options"] = options

            # Save the updated quiz
            mongo_q.db.quizes.replace_one({"_id": quiz_id}, quiz)

            return jsonify({"message": "Quiz updated successfully."}), 200

        else:
            return jsonify({"message": "Quiz not found."}), 404

    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500


# Delete quiz requires quiz id and creator id, we are not deleting quiz for real we just make it to not show to any one
@app.route('/delete_quizz/<string:quiz_id>/<string:creator_id>', methods = ['DELETE'])
def delete_quizz(quiz_id, creator_id):
    try:
        result = mongo_q.db.quizes.find_one({"_id": quiz_id})
        if result:
            if result["creator_id"] == creator_id:
                mongo_q.db.quizes.update_one({"_id": quiz_id}, {"$set": {"blocked": True}})
                return jsonify({"message": "Quiz deleted successfully."}), 200
            else:
                return jsonify({"message": "Unauthorized access. You do not have permission to delete this quiz."}), 403
        else:
            return jsonify({"message": "Quiz not found."}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500

# get quizes by profide filter of subjects, topics, subtopics and levels
@app.route('/get_quizzes_by_filter', methods=['GET'])
def get_quizzes_by_filter():
    try:
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        subtopic = request.form.get('subtopic')
        level = request.form.get('level')

        query = {}

        if subject:
            query["subject"] = subject
        if subject and topic:
            query = {
                "subject": subject,
                "topic": topic
            }
        if subject and topic and subtopic:
            query = {
                "subject": subject,
                "topic": topic,
                "subtopic": subtopic
            }
        if subject and topic and subtopic and level:
            query = {
                "subject": subject,
                "topic": topic,
                "subtopic": subtopic,
                "level": level
            }

        quizzes = mongo_q.db.quizes.find(query)

        if quizzes:
            quiz_list = list(quizzes)
            # Serialize the quiz_list to JSON using dumps
            quiz_json = dumps(quiz_list)
            return quiz_json, 200
        else:
            return jsonify({"message": "No quizzes found for the given criteria."}), 404

    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
