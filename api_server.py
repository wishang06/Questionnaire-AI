"""Flask API server for BondsAI frontend integration."""

import asyncio
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
import os
import glob
from server.AssessmentFileLoader import parse_assessment_file
from server.ApplicantManager import ApplicantManager

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Global instances to maintain conversation state
applicant_manager = ApplicantManager()

@app.route('/applicant')
def applicant():
    return app.send_static_file('applicant.html')

@app.route('/applicant/ai')
def applicant_ai():
    try:
        applicant_manager.start_conversation(request.remote_addr)
        return app.send_static_file('applicant_ai.html')
    
    except ValueError as e:
        if applicant_manager.get_applicant_status(request.remote_addr) == 'applying':
            return app.send_static_file('applicant_ai.html')
        
        return app.send_static_file('applicant_applied.html')

@app.route('/applicant/chat', methods=['POST'])
def applicant_chat():
    try:
        applicant_dance_assistant = applicant_manager.get_dance_assistant(request.remote_addr)
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get AI response
            ai_response = loop.run_until_complete(applicant_dance_assistant.chat(user_message))
            
            # Check if conversation is complete (ready for assessment)
            is_complete = applicant_dance_assistant.ready_for_assessment
            
            # If complete, generate assessment summary
            profile_data = None
            if is_complete:
                applicant_manager.stop_conversation_timer(request.remote_addr)
                conversation_duration = applicant_manager.get_conversation_duration(request.remote_addr)
                profile_data = {
                    "name": applicant_dance_assistant.candidate.name or "Candidate",
                    "conversation_count": applicant_dance_assistant.candidate.conversation_count,
                    "conversation_duration": conversation_duration,
                    "assessment_summary": "Dance assessment completed"
                }
            
            response = {
                "message": ai_response,
                "isComplete": is_complete,
                "profile": profile_data,
                "conversation_count": applicant_dance_assistant.candidate.conversation_count
            }
            
            return jsonify(response)
            
        finally:
            loop.close()

    except Exception as e:
        print(f"Error in dance assessment chat: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/applicant/end', methods=['POST'])
def end_applicant_conversation():
    try:
        applicant_manager.end_conversation(request.remote_addr)
        return jsonify({"message": "Conversation ended successfully"})
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 403

@app.route('/scripts/<path:filename>')
def send_script(filename):
    return app.send_static_file("scripts/" + filename)

@app.route('/styles/<path:filename>')
def send_styles(filename):
    return app.send_static_file("styles/" + filename)

@app.route('/recruiter')
def recruiter():
    return app.send_static_file("recruiter.html")

@app.route('/image/<path:filename>')
def send_icon(filename):
    return app.send_static_file("image/" + filename)

#Health check endpoint to verify SERVER is running
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "BondsAI API is running"})

# Get all job applicants and their assessment data
@app.route('/api/recruiter/applicants', methods=['GET'])
def get_applicants():
    try:
        assessments_dir = "assessments"
        applicants = []
        
        if not os.path.exists(assessments_dir):
            return jsonify({"applicants": []})
        
        # Get all assessment files (both old job assessments, new dance assessments, and quiz results)
        # Use a set to avoid duplicates if a file matches both patterns
        assessment_files = set(glob.glob(os.path.join(assessments_dir, "*_assessment_*.txt")))
        assessment_files.update(glob.glob(os.path.join(assessments_dir, "*_dance_assessment_*.txt")))
        assessment_files.update(glob.glob(os.path.join(assessments_dir, "*_quiz_*.txt")))
        
        for filepath in sorted(assessment_files):  # Sort for consistent ordering
            candidate_data = parse_assessment_file(filepath)
            if candidate_data:
                applicants.append(candidate_data)
        
        # Sort by final score (highest first), then by interview date (most recent first)
        applicants.sort(key=lambda x: (
            x.get('final_score', 0),
            x.get('interview_date', '')
        ), reverse=True)
        
        return jsonify({"applicants": applicants})
        
    except Exception as e:
        print(f"Error getting applicants: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/quiz')
def quiz():
    return app.send_static_file('quiz.html')

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    try:
        data = request.get_json()
        
        # Save quiz results to file
        assessments_dir = "assessments"
        if not os.path.exists(assessments_dir):
            os.makedirs(assessments_dir)
        
        from datetime import datetime
        name = data.get('name', 'Anonymous').strip()
        if name:
            name_part = "_".join(
                [
                    "".join(c for c in part if c.isalnum())
                    for part in name.split()
                ]
            )
            if not name_part:
                name_part = "candidate"
        else:
            name_part = "candidate"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name_part}_quiz_{timestamp}.txt"
        filepath = os.path.join(assessments_dir, filename)
        
        # Format quiz results
        results_content = f"""DANCE KNOWLEDGE QUIZ RESULTS
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Candidate Name: {name}
Score: {data.get('score', 0)}/{data.get('total', 10)} ({data.get('percentage', 0)}%)

=== QUIZ RESULTS ===

Overall Score: {data.get('score', 0)}/{data.get('total', 10)} ({data.get('percentage', 0)}%)

=== CATEGORY BREAKDOWN ===
"""
        
        category_names = {
            'rhythm': 'Rhythm & Timing',
            'knowledge': 'History & Origins',
            'terminology': 'Terminology',
            'technique': 'Technique',
            'style_knowledge': 'Style Knowledge',
            'creativity': 'Creativity'
        }
        
        category_scores = data.get('categoryScores', {})
        for cat, scores in category_scores.items():
            if scores.get('total', 0) > 0:
                percentage = round((scores.get('correct', 0) / scores.get('total', 1)) * 100)
                results_content += f"{category_names.get(cat, cat)}: {scores.get('correct', 0)}/{scores.get('total', 0)} ({percentage}%)\n"
        
        insights = data.get('insights', {})
        results_content += f"\n=== STRENGTHS ===\n"
        for strength in insights.get('strengths', []):
            results_content += f"- {strength}\n"
        
        results_content += f"\n=== AREAS FOR IMPROVEMENT ===\n"
        for weakness in insights.get('weaknesses', []):
            results_content += f"- {weakness}\n"
        
        results_content += f"\n=== RECOMMENDATIONS ===\n"
        for rec in insights.get('recommendations', []):
            results_content += f"- {rec}\n"
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(results_content)
        
        return jsonify({"message": "Quiz results saved successfully", "filepath": filepath})
        
    except Exception as e:
        print(f"Error saving quiz results: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.errorhandler(404)
def page_not_found(e):
    return app.send_static_file('404.html'), 404

if __name__ == '__main__':
    print("Starting Dance Assessment API Server...")
    print("Make sure you have set up your OpenAI API key in the .env file")
    print("Server will be available at http://localhost:8000")
    app.run(debug=True, host='0.0.0.0', port=8000)
