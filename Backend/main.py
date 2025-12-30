import os
import requests
import uuid
import random
import smtplib
import threading
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient
from flask_cors import CORS
from googleapiclient.discovery import build
from flask import Flask, request, jsonify, url_for, redirect, session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload 
from werkzeug.security import generate_password_hash, check_password_hash
from concurrent.futures import ThreadPoolExecutor
from orm import Admin, Session as DBSession
from Analytics import get_analytics_summary
from authlib.integrations.flask_client import OAuth
import pyotp
import pyqrcode
import base64
from io import BytesIO
from dotenv import load_dotenv
import chromadb
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

executor = ThreadPoolExecutor(max_workers=5)

CONNECTION_STRING = ""
client = MongoClient(CONNECTION_STRING)
db = client["recruitment_db"]
admin = db["admin"]
job_posting = db["job_posting"]
application_status = db["application_status"]
applications = db["applications"]

DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

script_dir = os.path.abspath(os.path.dirname(__file__))
drive_credentials_path = os.path.join(script_dir, 'Applications/google_drive/credentials.json')
drive_token_path = os.path.join(script_dir, 'Applications/google_drive/token.json')

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = ''
SENDER_PASSWORD = ''

# --- Google SSO Configuration ---
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Chatbot configuration
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY")
JINA_API_KEY = os.environ.get("JINA_API_KEY")

if not FIREWORKS_API_KEY:
    raise ValueError("Please set FIREWORKS_API_KEY environment variable")
if not JINA_API_KEY:
    raise ValueError("Please set JINA_API_KEY environment variable")

def create_query_embedding(query):
    """Create embedding for the user query using Jina AI"""
    url = 'https://api.jina.ai/v1/embeddings'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JINA_API_KEY}'
    }
    
    data = {
        'input': [query],
        'model': 'jina-embeddings-v3'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        embedding = result['data'][0]['embedding']
        
        return embedding
    except requests.exceptions.HTTPError as e:
        print(f"Error response: {response.text}")
        raise e

def retrieve_relevant_documents(query_embedding, n_results=3):
    """Retrieve relevant documents from ChromaDB"""
    client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        collection = client.get_collection(name="reports_collection")
    except:
        raise ValueError("Collection not found. Please run embeddings.py first")
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    return results

def generate_response(query, context_documents):
    """Generate response using Fireworks AI GPT model with retrieved context"""
    context = "\n\n".join([
        f"Document {i+1} (Source: {meta['source']}):\n{doc}"
        for i, (doc, meta) in enumerate(zip(
            context_documents['documents'][0],
            context_documents['metadatas'][0]
        ))
    ])
    
    prompt = f"""Based on the following context documents, please answer the user's question.
If the answer cannot be found in the context, say so.

Context:
{context}

Question: {query}

Answer:"""
    
    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    
    payload = {
        "model": "accounts/fireworks/models/gpt-oss-120b",
        "max_tokens": 2500,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORKS_API_KEY}"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        result = response.json()
        answer = result['choices'][0]['message']['content']
        
        return answer
    except requests.exceptions.HTTPError as e:
        print(f"Error response: {response.text}")
        raise e

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        user_query = request.json.get('query')
        
        if not user_query:
            return jsonify({"error": "Query is required"}), 400
        
        print(f"Received query: {user_query}")  # Debug log
        
        # Create embedding
        query_embedding = create_query_embedding(user_query)
        print("Embedding created successfully")  # Debug log
        
        # Retrieve relevant documents
        relevant_docs = retrieve_relevant_documents(query_embedding, n_results=15)
        print(f"Retrieved {len(relevant_docs['documents'][0])} documents")  # Debug log
        
        # Generate response
        answer = generate_response(user_query, relevant_docs)
        print("Response generated successfully")  # Debug log
        
        return jsonify({"response": answer})
        
    except ValueError as ve:
        print(f"ValueError: {str(ve)}")
        return jsonify({
            "error": "ChromaDB collection not found. Please run embeddings.py first to create the collection."
        }), 500
        
    except requests.exceptions.RequestException as re:
        print(f"Request error: {str(re)}")
        return jsonify({
            "error": f"API request failed: {str(re)}"
        }), 500
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()  # This will print the full stack trace
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500
    
def send_emails_to_candidates(candidate_reference, assessment_questions):
    
    if not candidate_reference:
        print("No candidates provided to send emails.")
        return

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print(f"Successfully logged in to {SMTP_SERVER}.")

        successful_sends = 0
        failed_sends = 0
        
        for name, data in candidate_reference.items():
            candidate_email = data.get('email')
            
            if not candidate_email:
                print(f"Skipping {name}: Email address is missing.")
                failed_sends += 1
                continue

            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = candidate_email
            msg['Subject'] = 'Your Online Assessment'
            
            body = f"""
            Dear {name},

            Thank you for your interest in this opportunity. We were impressed with your resume and would like to invite you to complete a brief online assessment.

            Please answer the following 5 questions:

            {assessment_questions}

            We look forward to receiving your responses.

            Best regards,

            The Recruitment Team
            """
            msg.attach(MIMEText(body, 'plain'))

            try:
                # 3. Send the email
                server.sendmail(SENDER_EMAIL, candidate_email, msg.as_string())
                print(f"Successfully sent email to {name} at {candidate_email}")
                successful_sends += 1
            except Exception as e:
                print(f"Failed to send email to {name} ({candidate_email}): {e}")
                failed_sends += 1

        # 4. Close the server connection
        server.quit()
        
    except Exception as e:
        print(f"An error occurred during SMTP connection or login: {e}")

def get_drive_service():
    drive_creds = None
    if os.path.exists(drive_token_path):
        drive_creds = Credentials.from_authorized_user_file(drive_token_path, DRIVE_SCOPES)

    if not drive_creds or not drive_creds.valid:
        if drive_creds and drive_creds.expired and drive_creds.refresh_token:
            drive_creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(drive_credentials_path, DRIVE_SCOPES)
            drive_creds = flow.run_local_server(port=0)
            
        with open(drive_token_path, 'w') as token:
            token.write(drive_creds.to_json())

    drive_service = build('drive', 'v3', credentials=drive_creds)
    return drive_service


def process_resume_task(application_id, filepath, original_filename, job_description, 
                       user_name, user_emailid, job_id, folder_id):
    try:
        
        application_status.update_one(
            {"application_id": application_id},
            {"$set": {"status": "processing", "updated_at": datetime.utcnow()}}
        )

        user_score = 0
        user_review = ""
        
        with open(filepath, 'rb') as f:
            files = {'file': (original_filename, f, 'application/pdf')}
            payload = {'job_description': job_description}
            response = requests.post('http://127.0.0.1:5001/process-resume', files=files, data=payload)
            response.raise_for_status()

            api_response = response.json()
            user_score = api_response.get('final_score', 0)
            user_review = api_response.get('profile_summary', '')
            
        drive_service = get_drive_service()

        file_metadata = {
            'name': original_filename,
            'parents': [folder_id]
        }

        media = MediaFileUpload(filepath, resumable=True)
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, size'
        ).execute()

        uploaded_file_id = uploaded_file.get('id')
        file_link = f"https://drive.google.com/file/d/{uploaded_file_id}/view"

        application_data = {
            "application_id": application_id,
            "job_id": job_id,
            "name": user_name,
            "email": user_emailid,
            "resume_link": file_link,
            "score": user_score,
            "review": user_review,
            "submitted_at": datetime.utcnow()
        }
        applications.insert_one(application_data)

        application_status.update_one(
            {"application_id": application_id},
            {
                "$set": {
                    "status": "completed",
                    "score": user_score,
                    "review": user_review,
                    "file_link": file_link,
                    "completed_at": datetime.utcnow()
                }
            }
        )

    except Exception as e:
        
        application_status.update_one(
            {"application_id": application_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                    "updated_at": datetime.utcnow()
                }
            }
        )


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    if admin.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'}), 409

    hashed_password = generate_password_hash(password)

    admin.insert_one({
        'name': name,
        'email': email,
        'password': hashed_password,
        'role': 'Applicant'
    })

    return jsonify({'message': 'User created successfully'}), 201


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    user = admin.find_one({'email': email})

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user'] = {
        'name': user.get('name'),
        'email': user.get('email'),
        'role': user.get('role')
    }

    return jsonify({
        'message': 'Sign-in successful',
        'user': {
            'name': user.get('name'),
            'email': user.get('email'),
            'role': user.get('role')
        }
    }), 200


@app.route('/employee-signin', methods=['POST'])
def employee_signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    db_session = DBSession()
    user = db_session.query(Admin).filter_by(username=username).first()

    if user and (password == user.password):
        if user.google_authenticator_secret:
            return jsonify({'redirect': '/verify-2fa', 'username': username})
        else:
            return jsonify({'redirect': '/setup-2fa', 'username': username})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/setup-2fa', methods=['GET'])
def setup_2fa():
    username = request.args.get('username')
    db_session = DBSession()
    user = db_session.query(Admin).filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'Invalid user for 2FA setup'}), 400

    secret = pyotp.random_base32()

    issuer_name = "Flask 2FA Demo"
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer_name)

    qr_code_svg = pyqrcode.create(uri)
    buffer = BytesIO()
    qr_code_svg.svg(buffer, scale=6)
    qr_code_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return jsonify({
        'secret_key': secret,
        'qr_code': f'data:image/svg+xml;base64,{qr_code_b64}'
    })

@app.route('/confirm-2fa', methods=['POST'])
def confirm_2fa():
    data = request.get_json()
    username = data.get('username')
    totp_code = data.get('totp_code')
    secret = data.get('secret')

    if not totp_code or not secret:
        return jsonify({'error': 'Missing required fields'}), 400

    totp = pyotp.TOTP(secret)
    if totp.verify(totp_code):
        db_session = DBSession()
        user = db_session.query(Admin).filter_by(username=username).first()
        user.google_authenticator_secret = secret
        db_session.commit()
        return jsonify({'message': '2FA setup successful'}), 200
    else:
        return jsonify({'error': 'Invalid TOTP code'}), 400

@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json()
    username = data.get('username')
    totp_code = data.get('totp_code')

    if not username or not totp_code:
        return jsonify({'error': 'Missing required fields'}), 400

    db_session = DBSession()
    user = db_session.query(Admin).filter_by(username=username).first()

    if not user or not user.google_authenticator_secret:
        return jsonify({'error': '2FA not set up for this user'}), 400

    totp = pyotp.TOTP(user.google_authenticator_secret)
    if totp.verify(totp_code):
        return jsonify({
            'message': 'Sign-in successful',
            'user': {
                'employee_id': user.employee_id,
                'username': user.username,
                'role': user.role
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid 2FA code'}), 401


@app.route("/jobs", methods=["GET"])
def get_all_jobs():
    all_jobs = list(job_posting.find())
    for job in all_jobs:
        job["_id"] = str(job["_id"])
    return jsonify(all_jobs)


@app.route("/jobs", methods=["POST"])
def create_job():
    data = request.get_json()
    if not data or "job_title" not in data or "job_description" not in data:
        return jsonify({"error": "Missing job_title or job_description"}), 400

    job_description = data["job_description"]
    job_title = data["job_title"]

    job_id = 'JOB' + str(random.randrange(10000000, 100000000))
    new_job = {
        "job_id": job_id,
        "job_title": job_title,
        "job_description": job_description,
        "date_posted": datetime.utcnow().strftime('%Y-%m-%d')
    }

    result = job_posting.insert_one(new_job)

    return jsonify({
        "message": "Job created successfully", 
        "inserted_id": str(result.inserted_id), 
        "job_id": new_job["job_id"]
    }), 201


@app.route("/jobs/<string:job_id>", methods=["GET"])
def get_job(job_id):
    job = job_posting.find_one({"job_id": job_id})
    if job:
        job["_id"] = str(job["_id"])
        return jsonify(job)
    return jsonify({"error": "Job not found"}), 404



# Delete Job Opening
@app.route("/jobs/<string:job_id>", methods=["DELETE"])
def delete_job(job_id):
    result = job_posting.delete_one({"job_id": job_id})
    if result.deleted_count > 0:
        return jsonify({"message": "Job deleted successfully"}), 200
    return jsonify({"error": "Job not found"}), 404


# Get Candidates for a Job with Filtering
@app.route('/jobs/<string:job_id>/candidates', methods=['GET'])
def get_filtered_candidates(job_id):
    min_score_str = request.args.get('min_score')
    
    if not min_score_str:
        return jsonify({"error": "min_score query parameter is required"}), 400
    
    try:
        min_score = int(min_score_str)
    except ValueError:
        return jsonify({"error": "min_score must be an integer"}), 400

    filtered_candidates = list(applications.find({
        "job_id": job_id,
        "score": {"$gte": min_score}
    }))
    
    if not filtered_candidates:
        return jsonify({"message": "No candidates found matching the criteria"}), 200

    candidate_reference = {}
    assessment_questions = ""
    for candidate in filtered_candidates:
        candidate.pop('_id', None)
        
        candidate_reference[candidate['name']] = {
            'email': candidate["email"]
        }

    oa_creator_url = 'http://127.0.0.1:5001/oa-creator'
    response = requests.post(oa_creator_url, json={'resume_link': candidate['resume_link']})
    response.raise_for_status()

    assessment_questions = response.text

    send_emails_to_candidates(candidate_reference, assessment_questions)

    return jsonify({
        "message": "Successfully processed candidates, sent emails, and generated assessment."
    }), 200


@app.route('/applicationform', methods=['POST'])
def submit_form():
    data = request.form
    user_name = data.get('name')
    user_emailid = data.get('email')
    job_id = data.get('job_id')
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    job = job_posting.find_one({"job_id": job_id})
    if not job:
        return jsonify({"error": "Job not found"}), 404
    job_description = job.get("job_description")

    folder_id = "1T0jvXp-AhR6NtXkmgsw5H8KR52duP-KS"

    application_id = str(uuid.uuid4())
    original_filename = file.filename
    unique_filename = f"{application_id}-{original_filename}"

    upload_folder = os.path.join(script_dir, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)

    application_status.insert_one({
        "application_id": application_id,
        "user_name": user_name,
        "user_email": user_emailid,
        "job_id": job_id,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    executor.submit(
        process_resume_task,
        application_id,
        filepath,
        original_filename,
        job_description,
        user_name,
        user_emailid,
        job_id,
        folder_id
    )

    print(f"Application {application_id} submitted to background processing queue")

    return jsonify({
        "message": "Application submitted successfully! Your application is being processed in the background.",
        "application_id": application_id,
        "status": "pending",
        "note": "You can check the status using the application_id"
    }), 202


@app.route('/application-status/<string:application_id>', methods=['GET'])
def check_application_status(application_id):
    app_status = application_status.find_one({"application_id": application_id})
    if not app_status:
        return jsonify({"error": "Application not found"}), 404
    app_status.pop('_id', None)
    return jsonify(app_status), 200


@app.route('/applications/<string:job_id>', methods=['GET'])
def get_applications_for_job(job_id):
    job_applications = list(applications.find({"job_id": job_id}))
    
    for app in job_applications:
        app.pop('_id', None)
        
    return jsonify(job_applications), 200

@app.route('/api/hr-analytics-summary', methods=['GET'])
def hr_analytics_summary():
    try:
        summary = get_analytics_summary()
        return jsonify(summary), 200
    except Exception as e:
        # Log the error for debugging
        print(f"Error in /api/hr-analytics-summary: {e}")
        # Return a generic error message
        return jsonify({"error": "An internal error occurred"}), 500

@app.route('/google-login')
def google_login():
    redirect_uri = url_for('google_auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth')
def google_auth():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')

    if user_info:
        user = admin.find_one({'email': user_info['email']})

        if not user:
            new_user = {
                'name': user_info['name'],
                'email': user_info['email'],
                'password': '', # No password for SSO users
                'role': 'Applicant'
            }
            admin.insert_one(new_user)
            user = new_user
        
        session['user'] = {
            'name': user.get('name'),
            'email': user.get('email'),
            'role': user.get('role')
        }

        return redirect('http://localhost:5173/career-page')

@app.route('/get-user')
def get_user():
    user = session.get('user')
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not logged in'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out successfully'}), 200

if __name__ == "__main__":
    try:
        app.run(debug=True, port=5002)
    finally:
        executor.shutdown(wait=True)
