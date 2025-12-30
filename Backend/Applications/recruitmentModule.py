import os
import io
from flask import Flask, request, jsonify
from crewai import Agent, Task, Crew, Process, LLM
import pdfplumber
import ast
import requests
import json
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload

app = Flask(__name__)

GOOGLE_API_KEY = ""
llm = LLM(api_key=GOOGLE_API_KEY, model="gemini/gemini-2.5-flash", temperature=0.5)

DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

script_dir = os.path.abspath(os.path.dirname(__file__))
drive_credentials_path = os.path.join(script_dir, 'google_drive/credentials.json')
drive_token_path = os.path.join(script_dir, 'google_drive/token.json')

def get_drive_service():
    """Get authenticated Google Drive service with proper error handling."""
    drive_creds = None
    
    # Load existing credentials
    if os.path.exists(drive_token_path):
        try:
            drive_creds = Credentials.from_authorized_user_file(drive_token_path, DRIVE_SCOPES)
        except Exception as e:
            print(f"Error loading token: {e}")
            # Delete invalid token
            os.remove(drive_token_path)
            drive_creds = None

    # Refresh or create new credentials
    if not drive_creds or not drive_creds.valid:
        if drive_creds and drive_creds.expired and drive_creds.refresh_token:
            try:
                drive_creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                # Delete invalid token and re-authenticate
                if os.path.exists(drive_token_path):
                    os.remove(drive_token_path)
                drive_creds = None
        
        if not drive_creds:
            # Create new credentials
            if not os.path.exists(drive_credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {drive_credentials_path}. "
                    "Please download it from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                drive_credentials_path, 
                DRIVE_SCOPES
            )
            drive_creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(drive_token_path, 'w') as token:
            token.write(drive_creds.to_json())

    drive_service = build('drive', 'v3', credentials=drive_creds)
    return drive_service

def extract_text_from_pdf(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

def get_file_content_from_drive(file_id):
    drive_service = get_drive_service()
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    fh.seek(0)
    return fh

def ats_filter_callback(output):
    try:
        result_dict = ast.literal_eval(output)
        ats_score = result_dict.get('ats_score')
        filter_result = result_dict.get('rule_based_filter_result')
        if ats_score is None or filter_result is None:
            print("Error: Required keys 'ats_score' or 'rule_based_filter_result' not found in the output.")
            return
        if ats_score < 70 or filter_result.lower() == 'failed':
            print("The candidate is rejected.")
        else:
            print("The candidate has passed the initial screening.")
    except (ValueError, SyntaxError) as e:
        print(f"Failed to parse the dictionary from the agent's output. Error: {e}")

def ai_detection(task_output):
    try:
        if hasattr(task_output, 'raw'):
            result_str = task_output.raw
        else:
            result_str = str(task_output)
        
        if 'Result = ' in result_str:
            dict_str = result_str.split('Result = ')[1].strip()
            if '}' in dict_str:
                dict_str = dict_str[:dict_str.rfind('}') + 1]
            result = ast.literal_eval(dict_str)
        else:
            result = ast.literal_eval(result_str)
        
        ai_detected = result.get('AI detection', False)
        
        if ai_detected:
            rejection_reasons = []
            if ai_detected:
                rejection_reasons.append("AI-generated content detected")
            
            rejection_message = {
                'status': 'REJECTED',
                'reason': f"Candidate rejected: {', '.join(rejection_reasons)}",
                'ai_detection': ai_detected,
                'action': 'STOP_EXECUTION'
            }
            
            print(f"CANDIDATE REJECTED: {', '.join(rejection_reasons)}")
            
            raise StopIteration(rejection_message)
                
        else:
            print("Candidate passed AI detection and information verification")
            return {
                'status': 'PASSED',
                'continue_execution': True,
                'ai_detection': ai_detected
            }
            
    except Exception as e:
        error_message = {
            'status': 'ERROR',
            'reason': f"Error parsing AI detection results: {str(e)}",
            'action': 'STOP_EXECUTION'
        }
        print(f"Error in callback: {str(e)}")
        raise StopIteration(error_message)

# Routes
@app.route('/process-resume', methods=['POST'])
def process_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    GOOGLE_API_KEY = ""
    llm = LLM(api_key=GOOGLE_API_KEY, model="gemini/gemini-2.5-flash", temperature=0.5)

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    job_description = request.form.get('job_description')
    if not job_description:
        return jsonify({"error": "job_description not found in request"}), 400

    if file:
        filename = file.filename
        
        script_dir = os.path.abspath(os.path.dirname(__file__))
        
        upload_folder = os.path.join(script_dir, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        resume_text = extract_text_from_pdf(filepath)
        jd_text = job_description

        ai_detection_agent = Agent(
            role="AI detection",
            goal="To find whether the document is created by AI or not.",
            backstory=(
                "You can understand whether the information given is AI generated or not. Use any internet tool to find out that."
            ),
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        ats_analyst_agent = Agent(
            role='ATS Analyst',
            goal='Calculate the ATS score and perform rule-based filtering on a resume.',
            backstory=(
                "You are a meticulous Applicant Tracking System (ATS) expert. Your job is to screen resumes for essential keywords and hard requirements (e.g., years of experience, specific certifications) to determine a preliminary score and eligibility. You are highly detail-oriented and follow rules precisely. Be very strict ATS Score checker and scrutinize the candidate very hardly. Your duty is to perform the task given very strictly."
            ),
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        skills_evaluator_agent = Agent(
            role='Skills Evaluator',
            goal='Score a resume on specific parameters: Education, Experience, Relevant Projects, and Technical Skills.',
            backstory=(
                "You are a seasoned technical recruiter with a keen eye for talent. You can read a resume "
                "and objectively assign scores based on key sections, understanding the difference between "
                "relevant and irrelevant experience. You have been hiring people since last 25 years and have seen ample amount of resumes. So you can scrutinize the resumes very good."
            ),
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        final_reviewer_agent = Agent(
            role='Final Reviewer',
            goal='Synthesize a comprehensive profile summary and a final overall score.',
            backstory=(
                "You are a Senior Hiring Manager responsible for making the final decision on candidates. "
                "You take all the data points—ATS score, individual parameter scores—and combine them into "
                "a clear, concise summary and a single, definitive final score out of 100."
            ),
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        ai_detection_task = Task(
            description=f"Analyze the document given:'{resume_text}', and find out whether the document was made using AI tools or not. Only mark it as True only if more than 70% of the content is generated by AI. Create a 3-4 line summary explaining the main concerns stating the reason about acceptance or rejection.",
            expected_output="Create a python dictionary in the format : Result = {\n"
                "    'AI detection': True/False,\n"
                "    'AI_reasons': 'Specific reasons for AI detection with examples',\n"
                "    'False_info_reasons': 'Specific reasons for false information with examples',\n"
                "    'rejection_summary': '3-4 line summary of main issues found'\n"
                "}",
            agent=ai_detection_agent,
            callback=ai_detection
        )

        ats_scoring_task = Task(
            description=f"Analyze the provided resume text given : '{resume_text}'and the job description given : '{jd_text}'. "
                "First, calculate a preliminary ATS score (out of 100) based on different parameters like - Professional keywords, Format of the CV, Integrity and relevancy of the content with the job description. Consider one factor very high that the technical skills provided should also align with the skills shown in the projects, experience and publications."
                "Second, apply rule-based filtering. Check if the education qualification fulfills the requirment of the job description provided or the experience or projects or publications is relevant to the job decsription provided. If either is not present, note that the candidate did not pass the filter. If the candidate doesn't pass the filter test, then the result of rule_based_filter_result will be failed."
                "The output should be 'ats_score' and 'rule_based_filter_result'.",
            expected_output="Create a python dictionary in the format :  Result = {'ats_score': 85, 'rule_based_filter_result': 'Passed'}. ",
            agent=ats_analyst_agent,
            callback=ats_filter_callback
        )

        parameter_scoring_task = Task(
            description=f"Using the resume text : '{resume_text}', and job decsription :'{jd_text}'score the candidate on a scale of 0-100 which would be floating values. For each parameter, decide the factors in floating values as the number of application being too high, the CV should have scores upto 4 decimal pointss for the following four parameters: "
                "1. Education: Score based on relevance and quality of degrees. The marking should on the basis of ranking of the college and it's reputation. The GPA also does play an important role in scoring the candidat's resume. "
                "2. Experience: Score based on years and relevance of professional experience. The experience should be relevant to the job decsription provided. More importantly the job title in the experience should be matching with the job description also. Other job experiences do not add any points in the final scoring. "
                "3. Relevant Projects: Score based on the number and impact of projects mentioned. The projects and publications shown in the resume text is one of the most iportant and should be scrutinized very hardly. The projects and publications should not only be relevant, but also shows that the candidate have adequate amount of pre-requisite knowledge that would be required in the job role according to the job description. If no live link or github link has been attached for the projects, give negative arking to that and reduce the overall score for this section. Also give additional points for candidates those who have mentioned about scholarships and publications. Publications are always prioritized over projects."
                "4. Technical Skills: Score based on the depth and breadth of listed technical skills. The technical skills should match with the projects and publications, then only it would be considered. Find whether the candidate really have those techincal skills portrayed in the projects and experiences and publication. Only consider those skills and if find it's relevance with the job decsription. Give the scores accordingly."
                "The output should be stored in a paragraph where each of the parameters and their scores are mentioned.",
            expected_output="The output should be stored in a paragraph where each of the parameters and their scores are mentioned.",
            agent=skills_evaluator_agent,
            context=[ats_scoring_task],
        )

        final_summary_task = Task(
            description=(
                "Analyze the output from the previous two tasks (the ATS score and the four parameter scores). "
                "First, create a concise, professional profile summary (3-4 sentences) that highlights the candidate's strengths. Show how the candidate is fit for the job and show how much relevant candidate have relevant experience or projects or publications. "
                "Second, calculate a final overall score out of 100. For each parameter, decide the factors in floating values as the number of application being too high, the CV should have scores upto 4 decimal pointss for the following four parameters. The final score should be a weighted average where: "
                "- ATS Score: 30% "
                "- Education: 10% "
                "- Experience: 25% "
                "- Relevant Projects: 20% "
                "- Technical Skills: 15% "
                "Present the final output as the summary and the final score in decimal points. in text format"
            ),
            expected_output="A dictionary containing 'profile_summary' (string) and 'final_score' (float).",
            agent=final_reviewer_agent,
            context=[ats_scoring_task, parameter_scoring_task]
        )

        recruiting_crew = Crew(
            agents=[ai_detection_agent, ats_analyst_agent, skills_evaluator_agent, final_reviewer_agent],
            tasks=[ai_detection_task, ats_scoring_task, parameter_scoring_task, final_summary_task],
            process=Process.sequential,
            verbose=True,
        )

        try:
            result = recruiting_crew.kickoff()
            
            result_str = result.raw if hasattr(result, 'raw') else str(result)
            print(f"Raw result: {result_str}")
            
            try:
                result_dict = ast.literal_eval(result_str)
            except (ValueError, SyntaxError):
                if '{' in result_str and '}' in result_str:
                    start_idx = result_str.find('{')
                    end_idx = result_str.rfind('}') + 1
                    dict_str = result_str[start_idx:end_idx]
                    result_dict = ast.literal_eval(dict_str)
                else:
                    raise ValueError("Could not parse result as dictionary")
            
            profile_summary = result_dict.get('profile_summary', 'No summary available')
            final_score = result_dict.get('final_score', 0)
            
            return jsonify({
                "final_score": final_score,
                "profile_summary": profile_summary,
            })
            
        except StopIteration as e:
            if hasattr(e, 'args') and len(e.args) > 0 and isinstance(e.args[0], dict):
                rejection_info = e.args[0]
                return jsonify({
                    "status": "rejected",
                    "reason": rejection_info.get('reason', 'Candidate rejected'),
                    "final_score": 0,
                    "profile_summary": rejection_info.get('reason', 'Candidate rejected due to AI detection')
                }), 200
            else:
                return jsonify({
                    "status": "rejected",
                    "reason": "Candidate rejected during screening",
                    "final_score": 0,
                    "profile_summary": "Candidate did not pass initial screening"
                }), 200
                
        except Exception as e:
            print(f"Error processing resume: {str(e)}")
            return jsonify({
                "error": f"Failed to process resume: {str(e)}",
                "final_score": 0,
                "profile_summary": "Error processing resume"
            }), 500




@app.route('/oa-creator', methods=['POST'])
def oa_creation():
    data = request.get_json()
    if not data or 'resume_link' not in data:
        return jsonify({"error": "resume_link not found in request"}), 400

    resume_link = data['resume_link']
    job_description = data.get('job_description', '')
    file_id = resume_link.split('/')[-2]

    try:
        pdf_content = get_file_content_from_drive(file_id)
        with pdfplumber.open(pdf_content) as pdf:
            resume_text = "".join(page.extract_text() for page in pdf.pages)

        # Define Agents
        Resume_Analyzer = Agent(
            role='Senior Resume Analyst',
            goal='Extract and analyze key information from candidate resumes including experience, projects, publications, and technical skills',
            backstory="You're an expert HR analyst with 15+ years of experience in talent acquisition. You have a keen eye for identifying relevant experience, understanding project complexities, and evaluating technical proficiencies. You excel at understanding the depth and breadth of a candidate's background and can distinguish between entry-level and senior-level expertise.",
            verbose=True,
            llm=llm
        )

        Experience_Question_Generator = Agent(
            role='Experience Assessment Specialist',
            goal='Create insightful, role-specific questions about candidate work experience',
            backstory="You're a seasoned hiring manager who has interviewed thousands of candidates across various industries. You specialize in crafting questions that reveal true professional competency, decision-making skills, and real-world problem-solving abilities. Your questions go beyond surface-level queries to uncover how candidates have handled complex situations, led initiatives, and driven results.",
            verbose=True,
            llm=llm
        )

        Project_Question_Generator = Agent(
            role='Technical Project Evaluator',
            goal='Develop challenging questions about candidate projects and research work',
            backstory="You're a technical lead and research mentor with deep expertise in evaluating academic and professional projects. You know how to ask questions that assess a candidate's understanding of project architecture, implementation challenges, research methodologies, and the impact of their work. You focus on the 'why' and 'how' rather than just the 'what'.",
            verbose=True,
            llm=llm
        )

        Skills_Question_Generator = Agent(
            role='Technical Skills Interviewer',
            goal='Create practical, hands-on questions to assess technical competencies',
            backstory="You're a principal engineer and technical interviewer who specializes in evaluating real-world application of technical skills. You design questions that test practical knowledge, problem-solving with specific technologies, and the ability to apply skills in realistic scenarios. Your questions reveal whether candidates truly understand their tools or just list them on resumes.",
            verbose=True,
            llm=llm
        )

        Question_Curator = Agent(
            role='Interview Question Curator',
            goal='Review, refine, and finalize the most impactful interview questions',
            backstory="You're the VP of Talent Acquisition with expertise in creating interview processes that accurately predict candidate success. You ensure questions are fair, non-discriminatory, challenging yet reasonable, and aligned with the candidate's experience level. You polish questions for clarity and impact while maintaining professional standards.",
            verbose=True,
            llm=llm
        )


        # Define Tasks
        analysis_task = Task(
            description=f'''Thoroughly analyze the following resume and extract:
            1. Educational background and level (Bachelor's, Master's, PhD, etc.)
            2. Years and types of work experience with specific roles and responsibilities
            3. Projects and publications with technical details and impact
            4. Technical skills with proficiency indicators
            5. Overall seniority level (entry, mid, senior, principal)
            
            Resume Content:
            {resume_text}
            
            Provide a structured analysis that will help other agents create appropriate interview questions.''',
            agent=Resume_Analyzer,
            expected_output='A comprehensive analysis document containing categorized information about education level, experience details, project/publication summaries, technical skills, and assessed seniority level of the candidate.'
        )

        experience_questions_task = Task(
            description='''Based on the resume analysis, create 2 challenging questions about the candidate's work experience. These questions should:
            - Focus on specific roles, responsibilities, or achievements mentioned in the resume
            - Probe decision-making, leadership, or problem-solving in past roles
            - Be appropriate for the candidate's seniority level
            - Reveal depth of experience beyond what's written
            - Avoid basic questions like "Tell me about yourself"
            
            Format: Provide exactly 2 questions, numbered.''',
            agent=Experience_Question_Generator,
            context=[analysis_task],
            expected_output='Exactly 2 well-crafted, role-specific questions about work experience that assess professional competency and real-world capabilities.'
        )

        project_questions_task = Task(
            description='''Based on the resume analysis, create 2 in-depth questions about the candidate's projects or publications. These questions should:
            - Reference specific projects or research work from the resume
            - Explore technical challenges, architectural decisions, or research methodologies
            - Assess understanding of impact, scalability, or contribution to the field
            - Be suited to the candidate's academic and professional level
            - Go beyond surface-level project descriptions
            
            Format: Provide exactly 2 questions, numbered.''',
            agent=Project_Question_Generator,
            context=[analysis_task],
            expected_output='Exactly 2 detailed questions about projects or publications that evaluate technical depth, problem-solving approach, and impact understanding.'
        )

        skills_question_task = Task(
            description='''Based on the resume analysis, create 1 practical question about the candidate's technical skills. This question should:
            - Focus on a key technical skill mentioned in the resume
            - Present a realistic scenario or problem requiring that skill
            - Test practical application rather than theoretical knowledge
            - Match the candidate's expertise level
            - Require demonstration of hands-on proficiency
            
            Format: Provide exactly 1 question.''',
            agent=Skills_Question_Generator,
            context=[analysis_task],
            expected_output='Exactly 1 practical, scenario-based question that assesses hands-on technical skill application.'
        )

        curation_task = Task(
            description='''Review all generated questions and create the final set of 5 interview questions:
            - Ensure 2 questions are about experience
            - Ensure 2 questions are about projects/publications
            - Ensure 1 question is about technical skills
            - Refine wording for clarity and professionalism
            - Verify questions are challenging yet fair
            - Ensure questions are appropriate for the candidate's level
            - Remove any redundancy or overlap
            
            Format the output as a clean, numbered list of exactly 5 questions ready to send to the candidate.''',
            agent=Question_Curator,
            context=[experience_questions_task, project_questions_task, skills_question_task],
            expected_output='A final, polished list of exactly 5 interview questions: 2 experience-based, 2 project/publication-based, and 1 technical skill-based, formatted professionally and ready for delivery to the hiring manager.'
        )

        # Create Crew
        crew = Crew(
            agents=[
                Resume_Analyzer,
                Experience_Question_Generator,
                Project_Question_Generator,
                Skills_Question_Generator,
                Question_Curator
            ],
            tasks=[
                analysis_task,
                experience_questions_task,
                project_questions_task,
                skills_question_task,
                curation_task
            ],
            verbose=True,
            llm=llm
        )


        result = crew.kickoff()
        
        return jsonify(result.raw)

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return jsonify({
            "error": f"Failed to process file: {str(e)}"
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
