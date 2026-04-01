import os
from dotenv import load_dotenv
load_dotenv()
from ollama import Client
import json
import re
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

stud_app = Flask(__name__)
#database setup
stud_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gaty3.db"
# creating database object
db = SQLAlchemy(stud_app)
#name age and course
class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    course = db.Column(db.String(50), nullable = False)

    def to_dict(self):
        return {
           "id" : self.id,
           "name" : self.name,
           "age" : self.age,
           "course" : self.course
         }

with stud_app.app_context():
    db.create_all()


@stud_app.route("/")
def home():
    return jsonify({"Greetings" : "Welcome to Our Homepage"})


@stud_app.route("/students", methods = ["GET"])
def get_studs():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])


@stud_app.route("/students/<int:student_id>", methods = ["GET"])
def get_stud(student_id):
    student= db.session.get(Student, student_id)
    if student:
        return jsonify(student.to_dict())
    else:
        return jsonify({"Error" : "Student not found"}), 404


@stud_app.route("/students", methods = ["POST"])
def add_stud():
    data = request.get_json()

    required_fields = ["name", "age", "course"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"Error": "Missing required fields"}), 400

    if not isinstance(data["age"], int):
        return jsonify({"Error": "Age must be an integer"}), 400

    new_student = Student(
       name = data["name"],
       age = data["age"],
       course = data["course"]
    )
    db.session.add(new_student)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": str(e)}), 500

    return jsonify({"Message" : "Student added successfully"}), 201


@stud_app.route("/students/<int:student_id>", methods = ["PUT"])
def update_stud(student_id):
    data = request.get_json()
    student = db.session.get(Student, student_id)

    if student:

        if "age" in data and not isinstance(data["age"], int):
            return jsonify({"Error": "Age must be an integer"}), 400

        student.name = data.get("name", student.name)
        student.age = data.get("age", student.age)
        student.course = data.get("course", student.course)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"Error": str(e)}), 500

        return jsonify(student.to_dict())

    else:
        return jsonify({"Error" : "Student not found"}), 404


@stud_app.route("/students/<int:student_id>", methods = ["DELETE"])
def del_stud(student_id):
    student = db.session.get(Student, student_id)
    if student:
        db.session.delete(student)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"Error": str(e)}), 500

        return jsonify({"Message" : "Student deleted successfully"})
    else:
        return jsonify({"Error" : "Student not found"}), 404


def parse_ollama_json(raw):
    # Extract JSON from inside ```json ... ``` if model wrapped it
    match = re.search(r'```json\s*(.*?)\s*```', raw, re.DOTALL)
    if match:
        raw = match.group(1)

    # Strip any leading/trailing whitespace
    raw = raw.strip()

    return json.loads(raw)



# ADDING THE AI LAYER
@stud_app.route("/students/<int:student_id>/study-tips", methods = ["POST"])
def stud_tips(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"Error" : "Student not found"}), 404


# setting up the connection
    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        return jsonify({"Error": "API key not configured"}), 500

    OLLAMA_HOST = os.getenv("OLLAMA_HOST")
    if not OLLAMA_HOST:
        return jsonify({"Error" : "OLLAMA_HOST not configured"}), 500

    client = Client(
        host=OLLAMA_HOST ,
        headers = {"Authorization" : "Bearer " + api_key}
    )

# calling ollama's AI
    try:
        response = client.chat(
            model="qwen3.5:397b-cloud",
            messages= [
            {
                "role" : "user",
                "content" : f"""You are an expert academic coach specializing in higher education.

                    A student is currently studying {student.course}.
                    
                    Generate exactly 2 study tips tailored specifically to this course. Each tip must be:
                    - Practical and immediately actionable
                    - Specific to the nature of {student.course} (not generic advice)
                    - Between 2-4 sentences in explanation
                    
                    Format your response exactly like this:
                    - [Tip Title]: [Explanation]
                    - [Tip Title]: [Explanation]
                    
                    Do not add any intro, outro, or extra commentary.
                    Do not use markdown, asterisks, hashtags, or special formatting. Use plain text only"""
            }
        ]
        )
    except Exception as e:
        return jsonify({"Error": str(e)}), 500

# extracting the text response
    try:
        tips = response.message.content
    except Exception:
        return jsonify({"Error": "Failed to parse AI response"}), 500

    return jsonify({
        "name" : student.name,
        "course" : student.course,
        "Study-tips" : tips
    })


@stud_app.route("/students/<int:student_id>/career-paths", methods= ["POST"])
def career_paths(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"Error" : "Student not found"}), 404

    api_key = os.getenv("OLLAMA_API_KEY")
    if not api_key:
        return jsonify({"Error" : "API key not configured"}), 500

    OLLAMA_HOST = os.getenv("ollama_host")
    if not OLLAMA_HOST:
        return jsonify({"Error" : "Ollama host not configured"}), 500

    try:
        client = Client(
            host=OLLAMA_HOST,
            headers= {"Authorization" : "Bearer " + api_key}
        )

        response = client.chat(
            model="qwen3.5:397b-cloud",
            messages= [
                {
                    "role" : "user",
                    "content" : f"""You are a career advisor. A student studies {student.course}.

                    Return ONLY a JSON object. No explanation. No markdown. No code blocks. No extra text.
                    
                    Exact format:
                    {{"careers": [{{"job_title": "", "key_skills": [], "salary_range": "", "industries": []}}]}}
                    
                    List 5 careers for this course."""
                }
            ]
        )

    except Exception as e:
        return jsonify({"Error": str(e)}), 500

    try:

        careers = response.message.content
        parsed = parse_ollama_json(careers)
        return jsonify(parsed), 200

    except json.JSONDecodeError:
        return jsonify({"error": "AI returned invalid JSON", "raw": raw}), 500



if __name__ == "__main__":
    stud_app.run(debug=True)







































