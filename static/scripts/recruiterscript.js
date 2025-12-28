let applicantsData = [];
let radarChart = null;

// Load applicants when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadApplicants();
});

async function loadApplicants() {
    const loading = document.getElementById('loading');
    const container = document.getElementById('applicants-container');
    const noApplicants = document.getElementById('no-applicants');
    
    loading.style.display = 'block';
    container.style.display = 'none';
    noApplicants.style.display = 'none';

    try {
        const response = await fetch('/api/recruiter/applicants');
        const data = await response.json();
        
        if (data.applicants && data.applicants.length > 0) {
            applicantsData = data.applicants;
            displayApplicants(data.applicants);
            container.style.display = 'block';
        } else {
            noApplicants.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading applicants:', error);
        noApplicants.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
}

function displayApplicants(applicants) {
    const grid = document.getElementById('applicants-grid');
    grid.innerHTML = '';

    applicants.forEach((applicant, index) => {
        const bubble = document.createElement('div');
        bubble.className = 'applicant-bubble';
        bubble.onclick = () => showCharacteristics(index);
        
        bubble.innerHTML = `
            <div class="applicant-name">${applicant.name || 'Anonymous'}</div>
            <div class="applicant-info">Assessment: ${applicant.interview_date}</div>
            <div class="applicant-info">Duration: ${applicant.conversation_duration}</div>
            <div class="applicant-score">Score: ${applicant.final_score || '0'}/100</div>
        `;
        
        grid.appendChild(bubble);
    });
}

function isDanceAssessment(applicant) {
    // Check if this is a dance assessment by looking for dance-specific fields
    return applicant.knowledge !== undefined || 
           applicant.creativity !== undefined || 
           applicant.preferences !== undefined ||
           (applicant.technical_skills && applicant.technical_skills.rhythm !== undefined);
}

function showCharacteristics(index) {
    const applicant = applicantsData[index];
    const modal = document.getElementById('characteristics-modal');
    const nameElement = document.getElementById('modal-candidate-name');
    const infoElement = document.getElementById('modal-candidate-info');
    const contentElement = document.getElementById('modal-characteristics-content');

    nameElement.textContent = applicant.name || 'Anonymous Candidate';
    infoElement.textContent = `Assessment completed on ${applicant.interview_date} • ${applicant.conversation_count} questions`;

    // Destroy existing chart if it exists
    if (radarChart) {
        radarChart.destroy();
        radarChart = null;
    }

    // Build characteristics content
    let content = '';

    if (isDanceAssessment(applicant)) {
        // Dance Assessment Display
        content = buildDanceAssessmentContent(applicant);
    } else {
        // Legacy Job Assessment Display
        content = buildJobAssessmentContent(applicant);
    }

    contentElement.innerHTML = content;
    modal.style.display = 'flex';

    // Create radar chart for dance assessments
    if (isDanceAssessment(applicant)) {
        // Wait for DOM to be ready and Chart.js to be loaded
        setTimeout(() => {
            if (typeof Chart !== 'undefined') {
                createRadarChart(applicant);
            } else {
                console.error('Chart.js is not loaded');
            }
        }, 200);
    }
}

function buildDanceAssessmentContent(applicant) {
    let content = '<div id="radar-chart-container" style="margin: 20px 0; text-align: center; height: 400px; position: relative;"><canvas id="ability-radar-chart" style="max-height: 400px;"></canvas></div>';

    // Technical Skills
    if (applicant.technical_skills) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Technical Skills</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Rhythm</div>
                        <div class="skill-score">${applicant.technical_skills.rhythm || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Coordination</div>
                        <div class="skill-score">${applicant.technical_skills.coordination || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Flexibility</div>
                        <div class="skill-score">${applicant.technical_skills.flexibility || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Musicality</div>
                        <div class="skill-score">${applicant.technical_skills.musicality || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Technique</div>
                        <div class="skill-score">${applicant.technical_skills.technique || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Knowledge
    if (applicant.knowledge) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Knowledge</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Dance History</div>
                        <div class="skill-score">${applicant.knowledge.dance_history || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Style Knowledge</div>
                        <div class="skill-score">${applicant.knowledge.style_knowledge || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Terminology</div>
                        <div class="skill-score">${applicant.knowledge.terminology || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Choreography Understanding</div>
                        <div class="skill-score">${applicant.knowledge.choreography_understanding || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Creativity
    if (applicant.creativity) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Creativity</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Improvisation</div>
                        <div class="skill-score">${applicant.creativity.improvisation || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Artistic Expression</div>
                        <div class="skill-score">${applicant.creativity.artistic_expression || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Originality</div>
                        <div class="skill-score">${applicant.creativity.originality || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Performance Quality</div>
                        <div class="skill-score">${applicant.creativity.performance_quality || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Preferences
    if (applicant.preferences) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Preferences</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Style Preference</div>
                        <div class="skill-score">${applicant.preferences.style_preference || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Learning Approach</div>
                        <div class="skill-score">${applicant.preferences.learning_approach || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Practice Commitment</div>
                        <div class="skill-score">${applicant.preferences.practice_commitment || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Performance Interest</div>
                        <div class="skill-score">${applicant.preferences.performance_interest || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Insights
    if (applicant.insights) {
        if (applicant.insights.strengths && applicant.insights.strengths.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Key Strengths</div>
                    <ul class="insights-list">
                        ${applicant.insights.strengths.map(strength => `<li>${strength}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (applicant.insights.areas_for_improvement && applicant.insights.areas_for_improvement.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Areas for Improvement</div>
                    <ul class="insights-list">
                        ${applicant.insights.areas_for_improvement.map(area => `<li>${area}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (applicant.insights.recommendations && applicant.insights.recommendations.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Personalized Recommendations</div>
                    <ul class="insights-list">
                        ${applicant.insights.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (applicant.insights.next_steps && applicant.insights.next_steps.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Next Steps</div>
                    <ul class="insights-list">
                        ${applicant.insights.next_steps.map(step => `<li>${step}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (applicant.insights.personalized_guidance && applicant.insights.personalized_guidance.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Personalized Guidance</div>
                    <div style="background: rgba(59, 130, 246, 0.1); border-radius: 10px; padding: 15px; white-space: pre-wrap; color: rgb(197, 228, 255); line-height: 1.6;">
                        ${applicant.insights.personalized_guidance[0]}
                    </div>
                </div>
            `;
        }
    }

    // AI Assessment Summary
    if (applicant.ai_assessment) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Full Diagnostic Report</div>
                <div style="background: rgba(59, 130, 246, 0.1); border-radius: 10px; padding: 15px; white-space: pre-wrap; color: rgb(197, 228, 255); max-height: 400px; overflow-y: auto;">
                    ${applicant.ai_assessment}
                </div>
            </div>
        `;
    }

    return content;
}

function buildJobAssessmentContent(applicant) {
    let content = '';

    // Technical Skills
    if (applicant.technical_skills) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Technical Skills</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Quantitative Reasoning</div>
                        <div class="skill-score">${applicant.technical_skills.quantitative_reasoning || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Programming</div>
                        <div class="skill-score">${applicant.technical_skills.programming || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Market Knowledge</div>
                        <div class="skill-score">${applicant.technical_skills.market_knowledge || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Data Analysis</div>
                        <div class="skill-score">${applicant.technical_skills.data_analysis || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Behavioral Traits
    if (applicant.behavioral_traits) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Behavioral Traits</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Problem Solving</div>
                        <div class="skill-score">${applicant.behavioral_traits.problem_solving || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Teamwork</div>
                        <div class="skill-score">${applicant.behavioral_traits.teamwork || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Initiative</div>
                        <div class="skill-score">${applicant.behavioral_traits.initiative || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Resilience</div>
                        <div class="skill-score">${applicant.behavioral_traits.resilience || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Adaptability</div>
                        <div class="skill-score">${applicant.behavioral_traits.adaptability || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Cultural Fit
    if (applicant.cultural_fit) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Cultural Fit</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Collaborative Thinking</div>
                        <div class="skill-score">${applicant.cultural_fit.collaborative_thinking || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Continuous Learning</div>
                        <div class="skill-score">${applicant.cultural_fit.continuous_learning || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Challenge Seeking</div>
                        <div class="skill-score">${applicant.cultural_fit.challenge_seeking || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Entrepreneurial Spirit</div>
                        <div class="skill-score">${applicant.cultural_fit.entrepreneurial_spirit || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Soft Skills
    if (applicant.soft_skills) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">Soft Skills</div>
                <div class="skills-grid">
                    <div class="skill-item">
                        <div class="skill-name">Communication</div>
                        <div class="skill-score">${applicant.soft_skills.communication || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Decision Making</div>
                        <div class="skill-score">${applicant.soft_skills.decision_making || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Time Management</div>
                        <div class="skill-score">${applicant.soft_skills.time_management || 0}/100</div>
                    </div>
                    <div class="skill-item">
                        <div class="skill-name">Leadership</div>
                        <div class="skill-score">${applicant.soft_skills.leadership || 0}/100</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Insights
    if (applicant.insights) {
        if (applicant.insights.strengths && applicant.insights.strengths.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Key Strengths</div>
                    <ul class="insights-list">
                        ${applicant.insights.strengths.map(strength => `<li>${strength}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (applicant.insights.weaknesses && applicant.insights.weaknesses.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Areas for Improvement</div>
                    <ul class="insights-list">
                        ${applicant.insights.weaknesses.map(weakness => `<li>${weakness}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (applicant.insights.recommendations && applicant.insights.recommendations.length > 0) {
            content += `
                <div class="characteristics-section">
                    <div class="section-title">Recommendations</div>
                    <ul class="insights-list">
                        ${applicant.insights.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
    }

    // AI Assessment Summary
    if (applicant.ai_assessment) {
        content += `
            <div class="characteristics-section">
                <div class="section-title">AI Assessment Summary</div>
                <div style="background: rgba(59, 130, 246, 0.1); border-radius: 10px; padding: 15px; white-space: pre-wrap; color: rgb(197, 228, 255);">${applicant.ai_assessment}</div>
            </div>
        `;
    }

    return content;
}

function createRadarChart(applicant) {
    const ctx = document.getElementById('ability-radar-chart');
    if (!ctx) {
        console.error('Radar chart canvas not found');
        return;
    }

    // Collect all ability scores for the radar chart
    const labels = [];
    const data = [];

    // Technical Skills
    if (applicant.technical_skills && 
        (applicant.technical_skills.rhythm || applicant.technical_skills.coordination || 
         applicant.technical_skills.flexibility || applicant.technical_skills.musicality || 
         applicant.technical_skills.technique)) {
        labels.push('Rhythm', 'Coordination', 'Flexibility', 'Musicality', 'Technique');
        data.push(
            applicant.technical_skills.rhythm || 0,
            applicant.technical_skills.coordination || 0,
            applicant.technical_skills.flexibility || 0,
            applicant.technical_skills.musicality || 0,
            applicant.technical_skills.technique || 0
        );
    }

    // Knowledge (average)
    if (applicant.knowledge && 
        (applicant.knowledge.dance_history || applicant.knowledge.style_knowledge || 
         applicant.knowledge.terminology || applicant.knowledge.choreography_understanding)) {
        const knowledgeScores = [
            applicant.knowledge.dance_history || 0,
            applicant.knowledge.style_knowledge || 0,
            applicant.knowledge.terminology || 0,
            applicant.knowledge.choreography_understanding || 0
        ].filter(s => s > 0);
        if (knowledgeScores.length > 0) {
            const knowledgeAvg = knowledgeScores.reduce((a, b) => a + b, 0) / knowledgeScores.length;
            labels.push('Knowledge');
            data.push(Math.round(knowledgeAvg));
        }
    }

    // Creativity (average)
    if (applicant.creativity && 
        (applicant.creativity.improvisation || applicant.creativity.artistic_expression || 
         applicant.creativity.originality || applicant.creativity.performance_quality)) {
        const creativityScores = [
            applicant.creativity.improvisation || 0,
            applicant.creativity.artistic_expression || 0,
            applicant.creativity.originality || 0,
            applicant.creativity.performance_quality || 0
        ].filter(s => s > 0);
        if (creativityScores.length > 0) {
            const creativityAvg = creativityScores.reduce((a, b) => a + b, 0) / creativityScores.length;
            labels.push('Creativity');
            data.push(Math.round(creativityAvg));
        }
    }

    // Preferences (average)
    if (applicant.preferences && 
        (applicant.preferences.style_preference || applicant.preferences.learning_approach || 
         applicant.preferences.practice_commitment || applicant.preferences.performance_interest)) {
        const preferencesScores = [
            applicant.preferences.style_preference || 0,
            applicant.preferences.learning_approach || 0,
            applicant.preferences.practice_commitment || 0,
            applicant.preferences.performance_interest || 0
        ].filter(s => s > 0);
        if (preferencesScores.length > 0) {
            const preferencesAvg = preferencesScores.reduce((a, b) => a + b, 0) / preferencesScores.length;
            labels.push('Engagement');
            data.push(Math.round(preferencesAvg));
        }
    }

    // Don't create chart if no data
    if (labels.length === 0 || data.length === 0) {
        console.warn('No data available for radar chart');
        return;
    }

    // Destroy existing chart if it exists
    if (radarChart) {
        radarChart.destroy();
    }

    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Dance Abilities',
                data: data,
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(59, 130, 246, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 1,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: 'rgba(197, 228, 255, 0.8)'
                    },
                    grid: {
                        color: 'rgba(197, 228, 255, 0.2)'
                    },
                    pointLabels: {
                        color: 'rgba(197, 228, 255, 1)',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: 'rgba(197, 228, 255, 1)',
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleColor: 'rgba(197, 228, 255, 1)',
                    bodyColor: 'rgba(197, 228, 255, 1)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }
            }
        }
    });
}

function closeModal() {
    const modal = document.getElementById('characteristics-modal');
    modal.style.display = 'none';
    
    // Destroy chart when modal closes
    if (radarChart) {
        radarChart.destroy();
        radarChart = null;
    }
}

// Close modal when clicking outside
document.getElementById('characteristics-modal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});
