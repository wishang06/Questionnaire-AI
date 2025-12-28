import re
import os
from datetime import datetime
from src.server.AIAssessmentCompiler import compile_AI_assessment

def parse_assessment_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic info from filename and content
        filename = os.path.basename(filepath)
        is_quiz = "_quiz_" in filename.lower()
        
        if is_quiz:
            name_match = re.search(r'^(.+?)_quiz_', filename)
        else:
            name_match = re.search(r'^(.+?)_(?:assessment|dance_assessment)_', filename)
        candidate_name = name_match.group(1).replace('_', ' ').title() if name_match else "Anonymous"
        
        # Extract interview date from filename
        if is_quiz:
            date_match = re.search(r'_quiz_(\d{8})_\d{6}\.txt$', filename)
        else:
            date_match = re.search(r'_(?:assessment|dance_assessment)_(\d{8})_\d{6}\.txt$', filename)
        if date_match:
            date_str = date_match.group(1)
            interview_date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
        else:
            interview_date = "Unknown"
        
        # Extract conversation count
        conversation_count = 0
        count_match = re.search(r'Interview Length: (\d+) exchanges', content)
        if count_match:
            conversation_count = int(count_match.group(1))

        # Extract conversation duration
        conversation_duration_match = re.search(r'Conversation Duration: (\d+)h (\d+)m (\d+)s', content)
        if conversation_duration_match:
            conversation_duration = f"{conversation_duration_match.group(1)}h {conversation_duration_match.group(2)}m {conversation_duration_match.group(3)}s"
        else:
            conversation_duration = "0h 0m 0s"

        final_score = 0
        final_score_match = re.search(r'Final Score: (\d+)', content.replace('**', ''))
        if final_score_match:
            final_score = int(final_score_match.group(1))
        
        # Check if this is a dance assessment, job assessment, or quiz (already set above)
        is_dance_assessment = "dance_assessment" in filename.lower()
        
        # Initialize default scores based on assessment type
        if is_dance_assessment:
            candidate_data = {
                "name": candidate_name,
                "interview_date": interview_date,
                "conversation_count": conversation_count,
                "conversation_duration": conversation_duration,
                "final_score": final_score,
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
                },
                "insights": {
                    "strengths": [],
                    "areas_for_improvement": [],
                    "recommendations": [],
                    "next_steps": [],
                    "personalized_guidance": []
                },
                "ai_assessment": ""
            }
        else:
            # Legacy job assessment format
            candidate_data = {
                "name": candidate_name,
                "interview_date": interview_date,
                "conversation_count": conversation_count,
                "conversation_duration": conversation_duration,
                "final_score": final_score,
                "technical_skills": {
                    "quantitative_reasoning": 0,
                    "programming": 0,
                    "market_knowledge": 0,
                    "data_analysis": 0
                },
                "behavioral_traits": {
                    "problem_solving": 0,
                    "teamwork": 0,
                    "initiative": 0,
                    "resilience": 0,
                    "adaptability": 0
                },
                "cultural_fit": {
                    "collaborative_thinking": 0,
                    "continuous_learning": 0,
                    "challenge_seeking": 0,
                    "entrepreneurial_spirit": 0
                },
                "soft_skills": {
                    "communication": 0,
                    "decision_making": 0,
                    "time_management": 0,
                    "leadership": 0
                },
                "insights": {
                    "strengths": [],
                    "weaknesses": [],
                    "recommendations": []
                },
                "ai_assessment": ""
            }
        
        # Try to extract AI assessment content (everything between the header and transcript)
        assessment_start = content.find("Generated on:")
        # Check for both "Full Interview Transcript:" (job assessments) and "Full Questionnaire Transcript:" (dance assessments)
        transcript_start = content.find("Full Interview Transcript:")
        if transcript_start == -1:
            transcript_start = content.find("Full Questionnaire Transcript:")
        
        # Handle quiz results (different format)
        if is_quiz:
            # Parse quiz results
            score_match = re.search(r'Score:\s*(\d+)/(\d+)\s*\((\d+)%\)', content)
            if score_match:
                candidate_data["quiz_score"] = int(score_match.group(1))
                candidate_data["quiz_total"] = int(score_match.group(2))
                candidate_data["quiz_percentage"] = int(score_match.group(3))
                candidate_data["final_score"] = int(score_match.group(3))
            
            # Parse category breakdown
            category_section = re.search(r'=== CATEGORY BREAKDOWN ===(.*?)(?=== STRENGTHS|$)', content, re.DOTALL)
            if category_section:
                category_text = category_section.group(1)
                for line in category_text.split('\n'):
                    if ':' in line and '/' in line:
                        parts = line.split(':')
                        if len(parts) == 2:
                            cat_name = parts[0].strip()
                            score_part = parts[1].strip()
                            score_match = re.search(r'(\d+)/(\d+)', score_part)
                            if score_match:
                                if "category_scores" not in candidate_data:
                                    candidate_data["category_scores"] = {}
                                candidate_data["category_scores"][cat_name] = {
                                    "correct": int(score_match.group(1)),
                                    "total": int(score_match.group(2))
                                }
            
            # Parse insights
            strengths_section = re.search(r'=== STRENGTHS ===(.*?)(?=== AREAS|=== RECOMMENDATIONS|$)', content, re.DOTALL)
            if strengths_section:
                strengths_text = strengths_section.group(1)
                candidate_data["insights"]["strengths"] = extract_list_items(strengths_text)
            
            weaknesses_section = re.search(r'=== AREAS FOR IMPROVEMENT ===(.*?)(?=== STRENGTHS|=== RECOMMENDATIONS|$)', content, re.DOTALL)
            if weaknesses_section:
                weaknesses_text = weaknesses_section.group(1)
                candidate_data["insights"]["areas_for_improvement"] = extract_list_items(weaknesses_text)
            
            recommendations_section = re.search(r'=== RECOMMENDATIONS ===(.*?)$', content, re.DOTALL)
            if recommendations_section:
                recommendations_text = recommendations_section.group(1)
                candidate_data["insights"]["recommendations"] = extract_list_items(recommendations_text)
            
            return candidate_data
        
        if assessment_start != -1 and transcript_start != -1:
            ai_assessment = content[assessment_start:transcript_start].strip()
            candidate_data["ai_assessment"] = compile_AI_assessment(ai_assessment)
            
            # Try to extract scores using regex patterns
            # Look for patterns like "Technical Skills Assessment (0-100 for each):"
            # followed by skill names and scores
            
            # Extract final score
            final_score_match = re.search(r'Final Score[:\s]+(\d+)', ai_assessment, re.IGNORECASE)
            if final_score_match:
                candidate_data["final_score"] = int(final_score_match.group(1))
            
            if is_dance_assessment:
                # Extract dance assessment scores
                # Look for "#### 1. Technical Skills Assessment" or "Technical Skills" section
                tech_section = re.search(r'(?:####\s*\d+\.\s*)?Technical Skills.*?(?=####\s*\d+\.\s*Knowledge|####\s*\d+\.\s*Creativity|####\s*\d+\.\s*Preferences|####\s*\d+\.\s*Overall|Knowledge Assessment|Creativity Assessment|Preferences Assessment|Overall Assessment|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if tech_section:
                    tech_text = tech_section.group(0)
                    candidate_data["technical_skills"]["rhythm"] = extract_score(tech_text, "rhythm")
                    candidate_data["technical_skills"]["coordination"] = extract_score(tech_text, "coordination")
                    candidate_data["technical_skills"]["flexibility"] = extract_score(tech_text, "flexibility")
                    candidate_data["technical_skills"]["musicality"] = extract_score(tech_text, "musicality")
                    candidate_data["technical_skills"]["technique"] = extract_score(tech_text, "technique")
                
                # Extract knowledge scores
                knowledge_section = re.search(r'(?:####\s*\d+\.\s*)?Knowledge.*?(?=####\s*\d+\.\s*Technical|####\s*\d+\.\s*Creativity|####\s*\d+\.\s*Preferences|####\s*\d+\.\s*Overall|Technical Skills|Creativity Assessment|Preferences Assessment|Overall Assessment|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if knowledge_section:
                    knowledge_text = knowledge_section.group(0)
                    candidate_data["knowledge"]["dance_history"] = extract_score(knowledge_text, "history")
                    candidate_data["knowledge"]["style_knowledge"] = extract_score(knowledge_text, "style")
                    candidate_data["knowledge"]["terminology"] = extract_score(knowledge_text, "terminology")
                    candidate_data["knowledge"]["choreography_understanding"] = extract_score(knowledge_text, "choreography")
                
                # Extract creativity scores
                creativity_section = re.search(r'(?:####\s*\d+\.\s*)?Creativity.*?(?=####\s*\d+\.\s*Technical|####\s*\d+\.\s*Knowledge|####\s*\d+\.\s*Preferences|####\s*\d+\.\s*Overall|Technical Skills|Knowledge Assessment|Preferences Assessment|Overall Assessment|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if creativity_section:
                    creativity_text = creativity_section.group(0)
                    candidate_data["creativity"]["improvisation"] = extract_score(creativity_text, "improvisation")
                    # Try both "artistic expression" and "artistic_expression"
                    artistic_score = extract_score(creativity_text, "artistic")
                    if artistic_score == 0:
                        artistic_score = extract_score(creativity_text, "expression")
                    candidate_data["creativity"]["artistic_expression"] = artistic_score
                    candidate_data["creativity"]["originality"] = extract_score(creativity_text, "originality")
                    candidate_data["creativity"]["performance_quality"] = extract_score(creativity_text, "performance")
                
                # Extract preferences scores
                preferences_section = re.search(r'(?:####\s*\d+\.\s*)?Preferences.*?(?=####\s*\d+\.\s*Technical|####\s*\d+\.\s*Knowledge|####\s*\d+\.\s*Creativity|####\s*\d+\.\s*Overall|Technical Skills|Knowledge Assessment|Creativity Assessment|Overall Assessment|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if preferences_section:
                    preferences_text = preferences_section.group(0)
                    candidate_data["preferences"]["style_preference"] = extract_score(preferences_text, "style")
                    candidate_data["preferences"]["learning_approach"] = extract_score(preferences_text, "learning")
                    # Try both "practice" and "commitment"
                    practice_score = extract_score(preferences_text, "practice")
                    if practice_score == 0:
                        practice_score = extract_score(preferences_text, "commitment")
                    candidate_data["preferences"]["practice_commitment"] = practice_score
                    # Try both "performance" and "interest"
                    perf_score = extract_score(preferences_text, "performance")
                    if perf_score == 0:
                        perf_score = extract_score(preferences_text, "interest")
                    candidate_data["preferences"]["performance_interest"] = perf_score
                
                # Extract insights from Overall Assessment section
                overall_section = re.search(r'(?:####\s*\d+\.\s*)?Overall Assessment.*?(?=---|Full|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if overall_section:
                    overall_text = overall_section.group(0)
                    
                    # Extract strengths (handle markdown bold: "- **Key Strengths**:")
                    strengths_match = re.search(r'-\s*\*\*(?:Key )?Strengths?\*\*[:\s]+(.*?)(?=-\s*\*\*Areas|-\s*\*\*Recommendations|-\s*\*\*Next|-\s*\*\*Personalized|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if not strengths_match:
                        # Try without markdown
                        strengths_match = re.search(r'(?:Key )?Strengths?[:\s]+(.*?)(?=Areas|Improvement|Recommendations|Next|Personalized|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if strengths_match:
                        strengths_text = strengths_match.group(1)
                        candidate_data["insights"]["strengths"] = extract_list_items(strengths_text)
                    
                    # Extract areas for improvement
                    weaknesses_match = re.search(r'-\s*\*\*Areas for Improvement\*\*[:\s]+(.*?)(?=-\s*\*\*Strengths|-\s*\*\*Recommendations|-\s*\*\*Next|-\s*\*\*Personalized|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if not weaknesses_match:
                        weaknesses_match = re.search(r'Areas for Improvement[:\s]+(.*?)(?=Strengths|Recommendations|Next|Personalized|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if weaknesses_match:
                        weaknesses_text = weaknesses_match.group(1)
                        candidate_data["insights"]["areas_for_improvement"] = extract_list_items(weaknesses_text)
                    
                    # Extract recommendations
                    recommendations_match = re.search(r'-\s*\*\*Personalized Recommendations?\*\*[:\s]+(.*?)(?=-\s*\*\*Strengths|-\s*\*\*Areas|-\s*\*\*Next|-\s*\*\*Personalized|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if not recommendations_match:
                        recommendations_match = re.search(r'Personalized Recommendations?[:\s]+(.*?)(?=Strengths|Areas|Next|Personalized|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if recommendations_match:
                        recommendations_text = recommendations_match.group(1)
                        candidate_data["insights"]["recommendations"] = extract_list_items(recommendations_text)
                    
                    # Extract next steps
                    next_steps_match = re.search(r'-\s*\*\*Next Steps?\*\*[:\s]+(.*?)(?=-\s*\*\*Strengths|-\s*\*\*Areas|-\s*\*\*Recommendations|-\s*\*\*Personalized|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if not next_steps_match:
                        next_steps_match = re.search(r'Next Steps?[:\s]+(.*?)(?=Strengths|Areas|Recommendations|Personalized|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if next_steps_match:
                        next_steps_text = next_steps_match.group(1)
                        candidate_data["insights"]["next_steps"] = extract_list_items(next_steps_text)
                    
                    # Extract personalized guidance
                    guidance_match = re.search(r'-\s*\*\*Personalized Guidance\*\*[:\s]+(.*?)(?=-\s*\*\*Strengths|-\s*\*\*Areas|-\s*\*\*Recommendations|-\s*\*\*Next|---|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if not guidance_match:
                        guidance_match = re.search(r'Personalized Guidance[:\s]+(.*?)(?=Strengths|Areas|Recommendations|Next|---|$)', overall_text, re.DOTALL | re.IGNORECASE)
                    if guidance_match:
                        guidance_text = guidance_match.group(1).strip()
                        # Clean up the guidance text
                        guidance_text = re.sub(r'\n+', ' ', guidance_text)
                        candidate_data["insights"]["personalized_guidance"] = [guidance_text[:500]]  # Limit length
            else:
                # Legacy job assessment extraction
                tech_section = re.search(r'Technical Skills.*?(?=Behavioral|Cultural|Soft|Overall|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if tech_section:
                    tech_text = tech_section.group(0)
                    candidate_data["technical_skills"]["quantitative_reasoning"] = extract_score(tech_text, "quantitative")
                    candidate_data["technical_skills"]["programming"] = extract_score(tech_text, "programming")
                    candidate_data["technical_skills"]["market_knowledge"] = extract_score(tech_text, "market")
                    candidate_data["technical_skills"]["data_analysis"] = extract_score(tech_text, "data")
                
                behavioral_section = re.search(r'Behavioral.*?(?=Technical|Cultural|Soft|Overall|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if behavioral_section:
                    behavioral_text = behavioral_section.group(0)
                    candidate_data["behavioral_traits"]["problem_solving"] = extract_score(behavioral_text, "problem")
                    candidate_data["behavioral_traits"]["teamwork"] = extract_score(behavioral_text, "teamwork")
                    candidate_data["behavioral_traits"]["initiative"] = extract_score(behavioral_text, "initiative")
                    candidate_data["behavioral_traits"]["resilience"] = extract_score(behavioral_text, "resilience")
                    candidate_data["behavioral_traits"]["adaptability"] = extract_score(behavioral_text, "adaptability")
                
                cultural_section = re.search(r'Cultural.*?(?=Technical|Behavioral|Soft|Overall|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if cultural_section:
                    cultural_text = cultural_section.group(0)
                    candidate_data["cultural_fit"]["collaborative_thinking"] = extract_score(cultural_text, "collaborative")
                    candidate_data["cultural_fit"]["continuous_learning"] = extract_score(cultural_text, "learning")
                    candidate_data["cultural_fit"]["challenge_seeking"] = extract_score(cultural_text, "challenge")
                    candidate_data["cultural_fit"]["entrepreneurial_spirit"] = extract_score(cultural_text, "entrepreneurial")
                
                soft_section = re.search(r'Soft Skills.*?(?=Technical|Behavioral|Cultural|Overall|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if soft_section:
                    soft_text = soft_section.group(0)
                    candidate_data["soft_skills"]["communication"] = extract_score(soft_text, "communication")
                    candidate_data["soft_skills"]["decision_making"] = extract_score(soft_text, "decision")
                    candidate_data["soft_skills"]["time_management"] = extract_score(soft_text, "time")
                    candidate_data["soft_skills"]["leadership"] = extract_score(soft_text, "leadership")
                
                strengths_match = re.search(r'(?:Key )?Strengths?[:\s]+(.*?)(?=Areas|Weaknesses|Recommendations|Cultural|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if strengths_match:
                    strengths_text = strengths_match.group(1)
                    candidate_data["insights"]["strengths"] = extract_list_items(strengths_text)
                
                weaknesses_match = re.search(r'(?:Areas for Improvement|Weaknesses?)[:\s]+(.*?)(?=Strengths|Recommendations|Cultural|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if weaknesses_match:
                    weaknesses_text = weaknesses_match.group(1)
                    candidate_data["insights"]["weaknesses"] = extract_list_items(weaknesses_text)
                
                recommendations_match = re.search(r'Recommendations?[:\s]+(.*?)(?=Strengths|Weaknesses|Cultural|$)', ai_assessment, re.DOTALL | re.IGNORECASE)
                if recommendations_match:
                    recommendations_text = recommendations_match.group(1)
                    candidate_data["insights"]["recommendations"] = extract_list_items(recommendations_text)
        
        return candidate_data
        
    except Exception as e:
        print(f"Error parsing assessment file {filepath}: {str(e)}")
        return None

# Extract a score for a specific skill from text.
def extract_score(text, skill_keyword):
    # Handle markdown bold format: "- **Rhythm**: 85" or "**Rhythm**: 85"
    # Pattern 1: "- **Skill Name**: 85" or "- **Skill**: 85"
    pattern = rf'-\s*\*\*{skill_keyword}[^*]*\*\*[:\s]+(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Pattern 2: "**Skill Name**: 85" or "**Skill**: 85" (without dash)
    pattern = rf'\*\*{skill_keyword}[^*]*\*\*[:\s]+(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Pattern 3: "- Skill Name: 85" or "- Skill: 85" (without markdown)
    pattern = rf'-\s*{skill_keyword}[^:]*:\s*(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # Pattern 4: "Skill Name: 85" or "Skill: 85" (without dash or markdown)
    pattern = rf'{skill_keyword}[^:]*:\s*(\d+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    return 0

# Extract list items from text (bullet points, numbered lists, etc.).
def extract_list_items(text):
    items = []
    
    # Split by lines and look for list patterns
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Remove common list markers (including markdown)
        line = re.sub(r'^[-*•]\s*', '', line)
        line = re.sub(r'^\d+\.\s*', '', line)
        # Remove markdown bold/italic
        line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)  # Remove **bold**
        line = re.sub(r'\*([^*]+)\*', r'\1', line)      # Remove *italic*
        line = line.strip()
        
        if line and len(line) > 5:  # Only include meaningful items
            items.append(line)
    
    return items[:10]  # Limit to 10 items (increased from 5)
