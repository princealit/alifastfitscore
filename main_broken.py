from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
import re
import time
try:
    import fitz  # PyMuPDF
    PDF_PROCESSING = True
except ImportError:
    PDF_PROCESSING = False

app = FastAPI()

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF"""
    if not PDF_PROCESSING:
        raise HTTPException(status_code=400, detail="PDF processing not available")
    
    text = ""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF processing failed: {str(e)}")
    
    return text.strip()

def calculate_fit_score(resume_text: str, job_description: str) -> dict:
    """Calculate fit score between resume and job"""
    start_time = time.time()
    
    # Score components
    education_score = 0
    experience_score = 0
    skills_score = 0
    match_score = 0
    
    # Elite education patterns
    education_patterns = [
        (r"\b(MIT|Stanford|Harvard|Berkeley|Caltech|Princeton|Yale)\b", 9.5),
        (r"\b(CMU|Carnegie Mellon|Waterloo|Georgia Tech)\b", 9.0),
        (r"\b(UCLA|USC|Michigan|Northwestern|Duke)\b", 8.0),
    ]
    
    # Elite company patterns  
    company_patterns = [
        (r"\b(Google|Meta|Facebook|Apple|Netflix|Amazon|Microsoft)\b", 9.5),
        (r"\b(Stripe|Airbnb|Uber|OpenAI|Anthropic)\b", 9.0),
        (r"\b(McKinsey|Bain|BCG|Goldman Sachs)\b", 8.5),
    ]
    
    # Technical skills
    skill_patterns = [
        (r"\b(Python|JavaScript|React|AWS|Kubernetes)\b", 2.0),
        (r"\b(machine learning|AI|deep learning)\b", 3.0),
        (r"\b(system design|distributed systems)\b", 2.5),
    ]
    
    # Calculate education score
    for pattern, score in education_patterns:
        if re.search(pattern, resume_text, re.IGNORECASE):
            education_score = max(education_score, score)
    
    # Calculate experience score
    for pattern, score in company_patterns:
        if re.search(pattern, resume_text, re.IGNORECASE):
            experience_score = max(experience_score, score)
    
    # Calculate skills score and job match
    resume_skills = []
    job_skills = []
    
    for pattern, score in skill_patterns:
        r_matches = re.findall(pattern, resume_text, re.IGNORECASE)
        j_matches = re.findall(pattern, job_description, re.IGNORECASE)
        
        if r_matches:
            skills_score += min(len(r_matches) * score, 10)
            resume_skills.extend(r_matches)
        
        if j_matches:
            job_skills.extend(j_matches)
        
        # Bonus for matching job requirements
        if r_matches and j_matches:
            match_score += min(len(set(r_matches) & set(j_matches)) * score, 8)
    
    # Calculate overall score
    overall = (education_score * 0.2 + experience_score * 0.3 + 
               skills_score * 0.3 + match_score * 0.2)
    
    # Decision logic
    if overall >= 8.5:
        decision = "STRONG HIRE"
        recommendation = "Excellent fit! Top-tier candidate with matching skills."
    elif overall >= 7.0:
        decision = "HIRE"
        recommendation = "Good fit with strong qualifications."
    elif overall >= 5.5:
        decision = "MAYBE"
        recommendation = "Decent fit but needs more evaluation."
    else:
        decision = "NO HIRE"
        recommendation = "Poor fit for this role."
    
    processing_time = time.time() - start_time
    
    return {
        "overall_score": round(overall, 1),
        "education_score": round(education_score, 1),
        "experience_score": round(experience_score, 1),
        "skills_score": round(skills_score, 1),
        "match_score": round(match_score, 1),
        "hire_decision": decision,
        "recommendation": recommendation,
        "processing_time": round(processing_time, 3),
        "resume_skills": list(set(resume_skills)),
        "job_skills": list(set(job_skills)),
        "resume_length": len(resume_text),
        "job_length": len(job_description)
    }

@app.get("/", response_class=HTMLResponse)
def get_home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 FitScore - AI Candidate Evaluation</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }
            .container { 
                max-width: 1000px; margin: 0 auto; background: white;
                border-radius: 20px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { color: #4f46e5; font-size: 3rem; margin-bottom: 10px; }
            .header p { color: #6b7280; font-size: 1.2rem; }
            .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }
            .form-group { margin-bottom: 25px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 1.1rem; }
            textarea { 
                width: 100%; padding: 15px; border: 2px solid #e5e7eb; 
                border-radius: 12px; font-size: 14px; min-height: 200px; resize: vertical;
            }
            .file-upload {
                width: 100%; padding: 20px; border: 2px dashed #e5e7eb;
                border-radius: 12px; text-align: center; cursor: pointer; transition: all 0.3s ease;
            }
            .file-upload:hover { border-color: #4f46e5; background: #f8fafc; }
            .file-upload input { display: none; }
            .analyze-btn {
                width: 100%; padding: 18px; background: #4f46e5; color: white;
                border: none; border-radius: 12px; font-size: 1.2rem; cursor: pointer;
                font-weight: 600; transition: all 0.3s ease;
            }
            .analyze-btn:hover { background: #4338ca; transform: translateY(-2px); }
            .result { margin-top: 40px; padding: 30px; background: #f8fafc; border-radius: 12px; }
            .score-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
            .score-card { 
                background: white; padding: 15px; border-radius: 12px; text-align: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .score-value { font-size: 1.5rem; font-weight: bold; margin-bottom: 5px; }
            .score-label { color: #6b7280; font-size: 0.85rem; }
            .decision { font-size: 1.8rem; font-weight: bold; text-align: center; margin: 20px 0; padding: 20px; border-radius: 12px; }
            .strong-hire { background: #dcfce7; color: #166534; }
            .hire { background: #dbeafe; color: #1d4ed8; }
            .maybe { background: #fef3c7; color: #92400e; }
            .no-hire { background: #fecaca; color: #b91c1c; }
            .recommendation { background: white; padding: 20px; border-radius: 12px; margin: 20px 0; }
            .skills { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
            .skill-tag { background: #4f46e5; color: white; padding: 4px 10px; border-radius: 15px; font-size: 0.8rem; }
            @media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 FitScore</h1>
                <p>AI-Powered Job-to-Candidate Fit Analysis</p>
            </div>
            
            <form id="fitScoreForm" enctype="multipart/form-data">
                <div class="form-grid">
                    <div class="form-group">
                        <label>📄 Job Description</label>
                        <textarea id="jobDescription" placeholder="Paste the complete job description here..." required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>📋 Resume Upload (PDF)</label>
                        <div class="file-upload" onclick="document.getElementById('resumeFile').click()">
                            <input type="file" id="resumeFile" accept=".pdf" required>
                            <div id="uploadText">
                                <p style="font-size: 1.1rem; margin-bottom: 10px;">📁 Click to upload PDF resume</p>
                                <p style="color: #6b7280; font-size: 0.9rem;">PDF files only</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="analyze-btn" id="analyzeBtn">
                    🔍 Analyze Job-Candidate Fit
                </button>
            </form>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            document.getElementById('resumeFile').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    document.getElementById('uploadText').innerHTML = 
                        '<p style="color: #4f46e5; font-weight: 600;">✅ ' + file.name + '</p>' +
                        '<p style="color: #6b7280; font-size: 0.9rem;">Ready to analyze</p>';
                }
            });

            document.getElementById('fitScoreForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const jobDesc = document.getElementById('jobDescription').value.trim();
                const resumeFile = document.getElementById('resumeFile').files[0];
                
                if (!jobDesc || !resumeFile) {
                    alert('Please provide both job description and resume file');
                    return;
                }
                
                const analyzeBtn = document.getElementById('analyzeBtn');
                analyzeBtn.innerHTML = '⏳ Analyzing...';
                analyzeBtn.disabled = true;
                
                const formData = new FormData();
                formData.append('job_description', jobDesc);
                formData.append('resume_file', resumeFile);
                
                try {
                    const response = await fetch('/analyze-fit', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        displayResult(result);
                    } else {
                        throw new Error(result.detail || 'Analysis failed');
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        '<div style="color: #ef4444; text-align: center; padding: 20px;"><h3>❌ Analysis Failed</h3><p>' + error.message + '</p></div>';
                    document.getElementById('result').style.display = 'block';
                } finally {
                    analyzeBtn.innerHTML = '🔍 Analyze Job-Candidate Fit';
                    analyzeBtn.disabled = false;
                }
            });
            
            function displayResult(result) {
                const decisionClass = result.hire_decision.toLowerCase().replace(/[^a-z]/g, '-');
                
                const html = \`
                    <div class="decision \${decisionClass}">
                        \${result.hire_decision}: \${result.overall_score}/10
                    </div>
                    
                    <div class="recommendation">
                        <h3 style="margin-bottom: 10px;">💡 Recommendation</h3>
                        <p>\${result.recommendation}</p>
                    </div>
                    
                    <div class="score-grid">
                        <div class="score-card">
                            <div class="score-value" style="color: #7c3aed;">\${result.education_score}</div>
                            <div class="score-label">Education</div>
                        </div>
                        <div class="score-card">
                            <div class="score-value" style="color: #2563eb;">\${result.experience_score}</div>
                            <div class="score-label">Experience</div>
                        </div>
                        <div class="score-card">
                            <div class="score-value" style="color: #dc2626;">\${result.skills_score}</div>
                            <div class="score-label">Skills</div>
                        </div>
                        <div class="score-card">
                            <div class="score-value" style="color: #16a34a;">\${result.match_score}</div>
                            <div class="score-label">Job Match</div>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 12px; margin: 20px 0;">
                        <h3 style="margin-bottom: 15px;">🎯 Resume Skills Found</h3>
                        <div class="skills">
                            \${result.resume_skills.map(skill => \`<span class="skill-tag">\${skill}</span>\`).join('')}
                        </div>
                    </div>
                    
                    <div style="text-align: center; color: #6b7280; margin-top: 20px;">
                        <p>⚡ Processed in \${result.processing_time}s</p>
                    </div>
                \`;
                
                document.getElementById('result').innerHTML = html;
                document.getElementById('result').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """

@app.post("/analyze-fit")
async def analyze_job_fit(
    job_description: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """Analyze fit between job description and resume PDF"""
    try:
        # Validate inputs
        if not job_description or len(job_description.strip()) < 50:
            raise HTTPException(status_code=400, detail="Job description must be at least 50 characters")
        
        if not resume_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Resume must be a PDF file")
        
        # Extract text from PDF
        pdf_bytes = await resume_file.read()
        resume_text = extract_pdf_text(pdf_bytes)
        
        if len(resume_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract sufficient text from PDF")
        
        # Calculate fit score
        result = calculate_fit_score(resume_text, job_description)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fitscore-complete", "version": "2.0.0"}
