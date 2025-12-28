// Quiz questions and answers
const QUIZ_QUESTIONS = [
    {
        question: "What is the basic rhythm pattern for a waltz?",
        options: [
            "1-2-3, 1-2-3 (triple time)",
            "1-2, 1-2 (duple time)",
            "1-2-3-4, 1-2-3-4 (quadruple time)",
            "1-2-3-4-5-6, 1-2-3-4-5-6 (sextuple time)"
        ],
        correct: 0,
        category: "rhythm"
    },
    {
        question: "Which dance style originated in Argentina?",
        options: [
            "Salsa",
            "Tango",
            "Flamenco",
            "Cha-cha"
        ],
        correct: 1,
        category: "knowledge"
    },
    {
        question: "What does 'plié' mean in ballet?",
        options: [
            "To jump",
            "To bend",
            "To turn",
            "To stretch"
        ],
        correct: 1,
        category: "terminology"
    },
    {
        question: "In ballroom dancing, what is the 'frame'?",
        options: [
            "The dance floor",
            "The position of the arms and upper body",
            "The music tempo",
            "The dance pattern"
        ],
        correct: 1,
        category: "technique"
    },
    {
        question: "Which dance style is characterized by sharp, angular movements and isolations?",
        options: [
            "Ballet",
            "Hip-hop",
            "Waltz",
            "Tango"
        ],
        correct: 1,
        category: "style_knowledge"
    },
    {
        question: "What is the term for dancing without a predetermined sequence of steps?",
        options: [
            "Choreography",
            "Improvisation",
            "Routine",
            "Sequence"
        ],
        correct: 1,
        category: "creativity"
    },
    {
        question: "In Latin dance, what does 'Cuban motion' refer to?",
        options: [
            "The hip movement",
            "The arm position",
            "The footwork",
            "The head position"
        ],
        correct: 0,
        category: "technique"
    },
    {
        question: "Which dance originated in the ballrooms of Vienna?",
        options: [
            "Tango",
            "Viennese Waltz",
            "Salsa",
            "Foxtrot"
        ],
        correct: 1,
        category: "knowledge"
    },
    {
        question: "What is the primary time signature for most swing dances?",
        options: [
            "2/4",
            "3/4",
            "4/4",
            "6/8"
        ],
        correct: 2,
        category: "rhythm"
    },
    {
        question: "In dance terminology, what does 'adagio' mean?",
        options: [
            "Fast tempo",
            "Slow tempo",
            "Medium tempo",
            "Very fast tempo"
        ],
        correct: 1,
        category: "terminology"
    }
];

let currentQuestion = 0;
let answers = [];
let userName = "";

// Initialize quiz
document.addEventListener('DOMContentLoaded', function() {
    renderQuestions();
    updateProgress();
    
    document.getElementById('submit-quiz').addEventListener('click', submitQuiz);
    document.getElementById('finish-quiz').addEventListener('click', finishQuiz);
    
    // Scroll to quiz section
    document.getElementById('quiz-section').scrollIntoView({ behavior: 'smooth' });
});

function renderQuestions() {
    const container = document.getElementById('questions-container');
    container.innerHTML = '';
    
    QUIZ_QUESTIONS.forEach((q, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-item';
        questionDiv.id = `question-${index}`;
        
        questionDiv.innerHTML = `
            <div class="question-text">${index + 1}. ${q.question}</div>
            <div class="options-container">
                ${q.options.map((option, optIndex) => `
                    <label class="option-label">
                        <input type="radio" name="question-${index}" value="${optIndex}" />
                        <span class="option-text">${option}</span>
                    </label>
                `).join('')}
            </div>
        `;
        
        container.appendChild(questionDiv);
    });
}

function updateProgress() {
    const answered = answers.filter(a => a !== null && a !== undefined).length;
    document.getElementById('quiz-progress').textContent = `Question ${answered + 1} of ${QUIZ_QUESTIONS.length}`;
}

function collectAnswers() {
    answers = [];
    QUIZ_QUESTIONS.forEach((q, index) => {
        const selected = document.querySelector(`input[name="question-${index}"]:checked`);
        answers.push(selected ? parseInt(selected.value) : null);
    });
}

function submitQuiz() {
    userName = document.getElementById('quiz-name').value.trim();
    
    if (!userName) {
        alert('Please enter your name before submitting.');
        return;
    }
    
    collectAnswers();
    
    const unanswered = answers.filter(a => a === null || a === undefined).length;
    if (unanswered > 0) {
        if (!confirm(`You have ${unanswered} unanswered question(s). Submit anyway?`)) {
            return;
        }
    }
    
    // Calculate results
    const results = calculateResults();
    
    // Save results to server
    saveQuizResults(results);
    
    // Display results
    displayResults(results);
}

function calculateResults() {
    let correct = 0;
    let total = QUIZ_QUESTIONS.length;
    const categoryScores = {
        rhythm: { correct: 0, total: 0 },
        knowledge: { correct: 0, total: 0 },
        terminology: { correct: 0, total: 0 },
        technique: { correct: 0, total: 0 },
        style_knowledge: { correct: 0, total: 0 },
        creativity: { correct: 0, total: 0 }
    };
    
    const wrongCategories = [];
    const correctCategories = [];
    
    QUIZ_QUESTIONS.forEach((q, index) => {
        const userAnswer = answers[index];
        const isCorrect = userAnswer === q.correct;
        
        if (isCorrect) {
            correct++;
            if (!correctCategories.includes(q.category)) {
                correctCategories.push(q.category);
            }
        } else {
            if (!wrongCategories.includes(q.category)) {
                wrongCategories.push(q.category);
            }
        }
        
        // Track category scores
        if (categoryScores[q.category]) {
            categoryScores[q.category].total++;
            if (isCorrect) {
                categoryScores[q.category].correct++;
            }
        }
    });
    
    const percentage = Math.round((correct / total) * 100);
    
    // Generate insights based on results
    const insights = generateInsights(correct, total, categoryScores, wrongCategories, correctCategories);
    
    return {
        name: userName,
        score: correct,
        total: total,
        percentage: percentage,
        categoryScores: categoryScores,
        wrongCategories: wrongCategories,
        correctCategories: correctCategories,
        insights: insights,
        answers: answers,
        timestamp: new Date().toISOString()
    };
}

function generateInsights(score, total, categoryScores, wrongCategories, correctCategories) {
    const insights = {
        strengths: [],
        weaknesses: [],
        recommendations: [],
        areas_to_focus: []
    };
    
    // Overall performance
    if (score >= 8) {
        insights.strengths.push("Excellent overall dance knowledge");
    } else if (score >= 6) {
        insights.strengths.push("Good foundational dance knowledge");
    } else {
        insights.weaknesses.push("Basic dance knowledge needs improvement");
    }
    
    // Category-specific insights
    const categoryNames = {
        rhythm: "Rhythm and Timing",
        knowledge: "Dance History and Origins",
        terminology: "Dance Terminology",
        technique: "Dance Technique",
        style_knowledge: "Dance Style Knowledge",
        creativity: "Creative Dance Concepts"
    };
    
    // Identify strong areas
    Object.keys(categoryScores).forEach(cat => {
        const catScore = categoryScores[cat];
        if (catScore.total > 0) {
            const catPercentage = (catScore.correct / catScore.total) * 100;
            if (catPercentage === 100) {
                insights.strengths.push(`Strong understanding of ${categoryNames[cat]}`);
            } else if (catPercentage < 50) {
                insights.weaknesses.push(`Needs improvement in ${categoryNames[cat]}`);
                insights.areas_to_focus.push(categoryNames[cat]);
            }
        }
    });
    
    // Generate recommendations
    if (wrongCategories.includes('terminology')) {
        insights.recommendations.push("Study dance terminology and vocabulary");
    }
    if (wrongCategories.includes('rhythm')) {
        insights.recommendations.push("Practice identifying and counting different time signatures");
    }
    if (wrongCategories.includes('knowledge')) {
        insights.recommendations.push("Learn about the history and origins of different dance styles");
    }
    if (wrongCategories.includes('technique')) {
        insights.recommendations.push("Focus on understanding dance technique and body positioning");
    }
    
    if (insights.recommendations.length === 0) {
        insights.recommendations.push("Continue expanding your dance knowledge across all areas");
        insights.recommendations.push("Consider taking dance classes to deepen your practical understanding");
    }
    
    return insights;
}

function displayResults(results) {
    document.getElementById('quiz-form').style.display = 'none';
    document.getElementById('quiz-results').style.display = 'block';
    
    const summary = document.getElementById('results-summary');
    summary.innerHTML = `
        <div class="score-display">
            <div class="score-number">${results.score}/${results.total}</div>
            <div class="score-percentage">${results.percentage}%</div>
        </div>
        <div class="score-label">Correct Answers</div>
    `;
    
    const content = document.getElementById('results-content');
    
    // Category breakdown
    let categoryHTML = '<div class="results-section"><h3>Category Breakdown</h3><div class="category-grid">';
    const categoryNames = {
        rhythm: "Rhythm & Timing",
        knowledge: "History & Origins",
        terminology: "Terminology",
        technique: "Technique",
        style_knowledge: "Style Knowledge",
        creativity: "Creativity"
    };
    
    Object.keys(results.categoryScores).forEach(cat => {
        const catScore = results.categoryScores[cat];
        if (catScore.total > 0) {
            const percentage = Math.round((catScore.correct / catScore.total) * 100);
            categoryHTML += `
                <div class="category-item">
                    <div class="category-name">${categoryNames[cat]}</div>
                    <div class="category-score">${catScore.correct}/${catScore.total} (${percentage}%)</div>
                </div>
            `;
        }
    });
    categoryHTML += '</div></div>';
    
    // Insights
    let insightsHTML = '<div class="results-section"><h3>Assessment Insights</h3>';
    
    if (results.insights.strengths.length > 0) {
        insightsHTML += '<div class="insight-group"><h4>Strengths</h4><ul>';
        results.insights.strengths.forEach(s => {
            insightsHTML += `<li>${s}</li>`;
        });
        insightsHTML += '</ul></div>';
    }
    
    if (results.insights.weaknesses.length > 0) {
        insightsHTML += '<div class="insight-group"><h4>Areas for Improvement</h4><ul>';
        results.insights.weaknesses.forEach(w => {
            insightsHTML += `<li>${w}</li>`;
        });
        insightsHTML += '</ul></div>';
    }
    
    if (results.insights.recommendations.length > 0) {
        insightsHTML += '<div class="insight-group"><h4>Recommendations</h4><ul>';
        results.insights.recommendations.forEach(r => {
            insightsHTML += `<li>${r}</li>`;
        });
        insightsHTML += '</ul></div>';
    }
    
    insightsHTML += '</div>';
    
    content.innerHTML = categoryHTML + insightsHTML;
}

async function saveQuizResults(results) {
    try {
        const response = await fetch('/api/quiz/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(results)
        });
        
        if (!response.ok) {
            console.error('Failed to save quiz results');
        }
    } catch (error) {
        console.error('Error saving quiz results:', error);
    }
}

function finishQuiz() {
    window.location.href = '/applicant';
}

