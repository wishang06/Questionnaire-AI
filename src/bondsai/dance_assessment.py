"""Dance Assessment Assistant for evaluating dance knowledge and preferences."""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .config import config
from server.DeltaTimeRecorder import DeltaTimeRecorder
import re

class DanceCandidate:
    """Represents a dance candidate with assessment data."""
    
    def __init__(self):
        """Initialize candidate profile."""
        self.name = ""
        self.dance_style = ""
        self.experience_level = ""
        self.preferences = {}
        self.conversation_count = 0
        self.conversation_duration = "0h 0m 0s"
        self.conversation_timer = DeltaTimeRecorder()
        
        # Dance assessment scores
        self.scores = {
            "technical_skills": {
                "rhythm": 0,
                "coordination": 0,
                "flexibility": 0,
                "musicality": 0,
                "technique": 0
            },
            "knowledge": {
                "dance_history": 0,
                "style_knowledge": 0,
                "terminology": 0,
                "choreography_understanding": 0
            },
            "creativity": {
                "improvisation": 0,
                "artistic_expression": 0,
                "originality": 0,
                "performance_quality": 0
            },
            "preferences": {
                "style_preference": 0,
                "learning_approach": 0,
                "practice_commitment": 0,
                "performance_interest": 0
            }
        }
        
        # Assessment insights
        self.insights = {
            "strengths": [],
            "areas_for_improvement": [],
            "recommendations": [],
            "next_steps": [],
            "personalized_guidance": []
        }
    
    def get_filename(self) -> str:
        """Generate filename for candidate assessment."""
        # Sanitize and fallback logic for candidate name
        name = self.name.strip() if self.name else ""
        if name and name.lower() != "unknown":
            # Remove special characters and extra spaces
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
        return f"{name_part}_dance_assessment_{timestamp}.txt"
    
    def calculate_final_score(self) -> int:
        """Calculate final assessment score out of 100."""
        total_score = 0
        category_weights = {
            "technical_skills": 0.30,
            "knowledge": 0.25,
            "creativity": 0.25,
            "preferences": 0.20
        }
        
        for category, weight in category_weights.items():
            category_scores = self.scores[category].values()
            if category_scores:
                category_avg = sum(category_scores) / len(category_scores)
                total_score += category_avg * weight
        
        return round(total_score)


class DanceAssessmentAssistant:
    """AI assistant for assessing dance knowledge and preferences."""
    
    def __init__(self):
        """Initialize the dance assessment assistant."""
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.messages: List[Dict[str, str]] = []
        self.model = config.openai_model
        self.temperature = config.openai_temperature
        self.max_tokens = config.openai_max_tokens
        self.candidate = DanceCandidate()
        self.is_first_message = True
        self.ready_for_assessment = False
        self.questions_asked = 0
        self.fixed_questions_complete = False
        
        # Fixed questions that must be asked
        self.fixed_questions = [
            "What is your name?",
            "What style of dance are you interested in?",
            "Do you have any previous experience in dancing?"
        ]
        self.current_fixed_question = 0
        
        # System prompt for dance assessment
        self.system_prompt = f"""You are a friendly and knowledgeable dance instructor conducting an interactive dance assessment questionnaire. Your role is to:

1. **Ask fixed questions first** (in order):
   - "What is your name?"
   - "What style of dance are you interested in?" (e.g., ballet, hip-hop, salsa, contemporary, ballroom, jazz, tap, etc.)
   - "Do you have any previous experience in dancing?" (ask about years, classes, performances, etc.)

2. **After fixed questions, ask adaptive technical questions** based on their answers:
   - If they mentioned a specific dance style, ask technical questions about that style
   - Ask about their knowledge of dance terminology, history, or choreography
   - Assess their understanding of rhythm, musicality, and timing
   - Explore their experience with improvisation and creativity
   - Ask about their practice habits and commitment level
   - Understand their performance goals and interests

3. **Assessment Areas to Cover:**
   - **Technical Skills**: Rhythm, Coordination, Flexibility, Musicality, Technique
   - **Knowledge**: Dance History, Style Knowledge, Terminology, Choreography Understanding
   - **Creativity**: Improvisation, Artistic Expression, Originality, Performance Quality
   - **Preferences**: Style Preference, Learning Approach, Practice Commitment, Performance Interest

4. **Conversation Style:**
   - Be warm, encouraging, and supportive
   - Ask one question at a time
   - Show genuine interest in their dance journey
   - After 8-10 total questions (3 fixed + 5-7 adaptive), naturally conclude

5. **After completing questions**, thank them and let them know their assessment will be generated.

Start with: "Hello! Welcome to the Dance Assessment Questionnaire. I'm here to learn about your dance knowledge and preferences. Let's begin! What is your name?" """

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
        if role == "user":
            self.candidate.conversation_count += 1
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.messages.clear()
        self.candidate = DanceCandidate()
        self.is_first_message = True
        self.ready_for_assessment = False
        self.questions_asked = 0
        self.fixed_questions_complete = False
        self.current_fixed_question = 0
    
    async def generate_assessment_report(self) -> str:
        """Generate comprehensive dance assessment report using AI."""
        try:
            assessment_prompt = f"""Based on this dance assessment conversation, create a detailed diagnostic report for the candidate.

Conversation:
{chr(10).join([f"{msg['role'].upper()}: {msg['content']}" for msg in self.messages])}

Please provide a comprehensive assessment including:

1. **Technical Skills Assessment** (0-100 for each):
   - Rhythm: Ability to keep time and follow musical beats
   - Coordination: Body control and movement precision
   - Flexibility: Range of motion and physical capability
   - Musicality: Understanding and connection to music
   - Technique: Proper form and execution

2. **Knowledge Assessment** (0-100 for each):
   - Dance History: Understanding of dance evolution and cultural context
   - Style Knowledge: Depth of knowledge about their preferred dance style(s)
   - Terminology: Understanding of dance terms and vocabulary
   - Choreography Understanding: Ability to learn and remember sequences

3. **Creativity Assessment** (0-100 for each):
   - Improvisation: Ability to create movements spontaneously
   - Artistic Expression: Emotional and expressive capabilities
   - Originality: Unique style and creative thinking
   - Performance Quality: Stage presence and audience engagement

4. **Preferences Assessment** (0-100 for each):
   - Style Preference: Alignment with their chosen dance style
   - Learning Approach: How they prefer to learn (visual, auditory, kinesthetic)
   - Practice Commitment: Dedication and consistency
   - Performance Interest: Enthusiasm for performing

5. **Overall Assessment**:
   - Final Score (0-100)
   - Key Strengths (3-5 bullet points)
   - Areas for Improvement (3-5 bullet points)
   - Personalized Recommendations (3-5 specific suggestions)
   - Next Steps (3-5 actionable items)
   - Personalized Guidance (encouraging message with specific advice)

Format the response clearly with sections and scores, in the following example format:

### Dance Assessment Diagnostic Report

#### 1. Technical Skills Assessment
- **Rhythm**: (score)
  - (insight)
- **Coordination**: (score)
  - (insight)
- **Flexibility**: (score)
  - (insight)
- **Musicality**: (score)
  - (insight)
- **Technique**: (score)
  - (insight)

#### 2. Knowledge Assessment
- **Dance History**: (score)
  - (insight)
- **Style Knowledge**: (score)
  - (insight)
- **Terminology**: (score)
  - (insight)
- **Choreography Understanding**: (score)
  - (insight)

#### 3. Creativity Assessment
- **Improvisation**: (score)
  - (insight)
- **Artistic Expression**: (score)
  - (insight)
- **Originality**: (score)
  - (insight)
- **Performance Quality**: (score)
  - (insight)

#### 4. Preferences Assessment
- **Style Preference**: (score)
  - (insight)
- **Learning Approach**: (score)
  - (insight)
- **Practice Commitment**: (score)
  - (insight)
- **Performance Interest**: (score)
  - (insight)

#### 5. Overall Assessment
- **Final Score**: (score)
- **Key Strengths**:
  - (insight)
- **Areas for Improvement**:
  - (insight)
- **Personalized Recommendations**:
  - (insight)
- **Next Steps**:
  - (insight)
- **Personalized Guidance**:
  (encouraging message with specific advice)

"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": assessment_prompt}],
                temperature=0.3,
                max_tokens=2000,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating assessment: {str(e)}"
    
    async def save_assessment_to_file(self) -> str:
        """Save the assessment report to a text file."""
        try:
            # Ensure assessments directory exists
            assessments_dir = "assessments"
            if not os.path.exists(assessments_dir):
                os.makedirs(assessments_dir)
            
            # Generate filename
            filename = self.candidate.get_filename()
            filepath = os.path.join(assessments_dir, filename)
            
            # Generate AI assessment
            ai_assessment = await self.generate_assessment_report()
            
            # Create assessment content
            assessment_content = f"""DANCE ASSESSMENT DIAGNOSTIC REPORT
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Questionnaire Length: {self.candidate.conversation_count} exchanges
Conversation Duration: {self.candidate.conversation_duration}

{ai_assessment}

---
Full Questionnaire Transcript:
"""
            
            # Add conversation history
            for i, message in enumerate(self.messages, 1):
                assessment_content += f"\n{i}. {message['role'].upper()}: {message['content']}\n"
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(assessment_content)
            
            return filepath
            
        except Exception as e:
            return f"Error saving assessment: {str(e)}"
    
    async def extract_candidate_name(self) -> None:
        """Extract candidate name from the first user message."""
        name = (self.candidate.name or "").strip()
        user_msgs = [m["content"] for m in self.messages if m["role"] == "user"]
        if (name and name.lower() != "unknown") or not user_msgs:
            return
        first_msg = user_msgs[0].strip()
        extracted_name = None
        # Try common intro patterns
        patterns = [
            r"my name is ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"i am ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"i'm ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"this is ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"it's ([A-Za-z][a-zA-Z\-']*(?: [A-Za-z][a-zA-Z\-']*){0,2})",
            r"([A-Za-z][a-zA-Z\-']* [A-Za-z][a-zA-Z\-']*) here",
        ]
        for pat in patterns:
            match = re.search(pat, first_msg, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                break
        # If not found, extract first two alphabetic words
        if not extracted_name:
            words = [w for w in first_msg.split() if w.isalpha() and len(w) > 1]
            if words:
                extracted_name = words[0]
                if len(words) > 1:
                    extracted_name += f" {words[1]}"
        # Fallback to OpenAI
        if not extracted_name:
            try:
                name_extraction_prompt = f"""Based on the following response, what is the person's name?\n\nResponse:\n{first_msg}\n\nPlease respond with just the person's first and last name, or "Unknown" if no name was mentioned."""
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": name_extraction_prompt}],
                    temperature=0.1,
                    max_tokens=50,
                )
                extracted_name = response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error extracting candidate name: {str(e)}")
                extracted_name = None
        # Only accept if valid
        if (
            extracted_name
            and extracted_name.lower() != "unknown"
            and len(extracted_name.split()) <= 3
            and any(c.isalpha() for c in extracted_name)
        ):
            self.candidate.name = extracted_name
            print(f"[DEBUG] Candidate name set: {self.candidate.name}")

    async def chat(self, user_input: str = None) -> str:
        """Send a message to the AI and get a response."""
        
        # Add user message to history
        if user_input:
            self.add_message("user", user_input)
            
            # Extract candidate name after first user message
            user_msg_count = len([m for m in self.messages if m["role"] == "user"])
            if user_msg_count == 1:
                await self.extract_candidate_name()
        
        # Check if conversation is ready to end (8-12 exchanges)
        if self.candidate.conversation_count >= 8 and not self.ready_for_assessment:
            self.candidate.conversation_timer.update()
            self.candidate.conversation_duration = self.candidate.conversation_timer.get_delta_str()
            self.ready_for_assessment = True
            # Save assessment to file
            filepath = await self.save_assessment_to_file()
            ending_message = f"Thank you for completing the dance assessment questionnaire! Your responses have been recorded and a personalized diagnostic report has been generated.\n\nI'll review your answers and provide you with detailed feedback, recommendations, and next steps. Keep dancing! 💃🕺"
            self.add_message("assistant", ending_message)
            return ending_message
        
        # Force end if too long (15+ exchanges)
        if self.candidate.conversation_count >= 15 and not self.ready_for_assessment:
            self.ready_for_assessment = True
            filepath = await self.save_assessment_to_file()
            ending_message = f"Thank you for completing the dance assessment questionnaire! Your responses have been recorded and a personalized diagnostic report has been generated.\n\nI'll review your answers and provide you with detailed feedback, recommendations, and next steps. Keep dancing! 💃🕺"
            self.add_message("assistant", ending_message)
            return ending_message
        
        # Prepare messages for OpenAI API with system prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.messages)
        
        try:
            # Make API call to OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            # Extract AI response
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            self.add_message("assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            error_msg = f"Error communicating with OpenAI: {str(e)}"
            self.add_message("assistant", error_msg)
            return error_msg

