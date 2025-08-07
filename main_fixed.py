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
    """Calculate fit score between resume and job - FIXED VERSION"""
    start_time = time.time()
    
    # Score components
    education_score = 0
    experience_score = 0
    skills_score = 0
    match_score = 0
    achievements_score = 0
    
    # EXPANDED education patterns (all fields)
    education_patterns = [
        (r"\b(MIT|Stanford|Harvard|Berkeley|UC Berkeley|Caltech|Princeton|Yale|Columbia|Cornell|UPenn)\b", 9.5),
        (r"\b(CMU|Carnegie Mellon|Waterloo|Georgia Tech|UIUC|University of Illinois)\b", 9.0),
        (r"\b(UCLA|USC|Michigan|Northwestern|Duke|Brown|Dartmouth|Rice|UCSD)\b", 8.5),
        (r"\b(UT Austin|University of Washington|UW|Virginia Tech|Purdue|TAMU|Texas A&M)\b", 8.0),
        (r"\b(Penn State|Ohio State|University of Florida|Arizona State|NC State)\b", 7.5),
    ]
    
    # EXPANDED company patterns (all industries)
    company_patterns = [
        # Tech Giants
        (r"\b(Google|Meta|Facebook|Apple|Netflix|Amazon|Microsoft|FAANG)\b", 9.5),
        (r"\b(Stripe|Airbnb|Uber|OpenAI|Anthropic|SpaceX|Tesla|Palantir)\b", 9.0),
        # Consulting & Finance
        (r"\b(McKinsey|Bain|BCG|Goldman Sachs|JP Morgan|Morgan Stanley|Deloitte|PwC)\b", 8.5),
        # Engineering & Manufacturing
        (r"\b(Boeing|Lockheed Martin|Raytheon|General Electric|GE|Siemens|3M|Honeywell)\b", 8.5),
        (r"\b(Ford|GM|General Motors|Toyota|Honda|BMW|Mercedes|Volkswagen)\b", 8.0),
        # Startups
        (r"\b(startup|scale-up|Series A|Series B|YC|Y Combinator)\b", 7.5),
    ]
    
    # COMPREHENSIVE skills patterns
    skill_patterns = [
        # Software Engineering
        (r"\b(Python|JavaScript|TypeScript|Java|C\+\+|Go|Rust)\b", 1.5),
        (r"\b(React|Angular|Vue|Node\.js|Django|Flask)\b", 1.5),
        (r"\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins)\b", 2.0),
        (r"\b(machine learning|AI|deep learning|TensorFlow|PyTorch)\b", 2.5),
        # Mechanical Engineering  
        (r"\b(CAD|SolidWorks|AutoCAD|CATIA|Fusion 360|Inventor)\b", 2.0),
        (r"\b(mechanical design|product design|manufacturing|machining|CNC)\b", 2.0),
        (r"\b(robotics|automation|actuator|sensor|control systems)\b", 2.5),
        (r"\b(MATLAB|Simulink|LabVIEW|embedded systems)\b", 2.0),
        # General Skills
        (r"\b(project management|team leadership|cross-functional)\b", 1.0),
        (r"\b(operations|process improvement|innovation)\b", 1.0),
    ]
    
    # Achievements patterns
    achievement_patterns = [
        (r"\b(PhD|patent|publication|research|startup|founder)\b", 1.5),
        (r"\b(award|scholarship|summa cum laude|magna cum laude)\b", 1.0),
        (r"\b(hackathon|winner|competition|top 1%|top 5%)\b", 1.0),
    ]
    
    # Calculate education score (max from patterns)
    for pattern, score in education_patterns:
        if re.search(pattern, resume_text, re.IGNORECASE):
            education_score = max(education_score, score)
    
    # Calculate experience score (max from patterns)  
    for pattern, score in company_patterns:
        if re.search(pattern, resume_text, re.IGNORECASE):
            experience_score = max(experience_score, score)
    
    # Calculate skills score (accumulate but cap at 10)
    resume_skills = []
    job_skills = []
    
    for pattern, score in skill_patterns:
        r_matches = re.findall(pattern, resume_text, re.IGNORECASE)
        j_matches = re.findall(pattern, job_description, re.IGNORECASE)
        
        if r_matches:
            skills_score += len(r_matches) * score
            resume_skills.extend(r_matches)
        
        if j_matches:
            job_skills.extend(j_matches)
        
        # Bonus for matching job requirements
        if r_matches and j_matches:
            match_score += len(set(r_matches) & set(j_matches)) * score
    
    # Calculate achievements score
    for pattern, score in achievement_patterns:
        found = re.findall(pattern, resume_text, re.IGNORECASE)
        if found:
            achievements_score += len(found) * score
    
    # CRITICAL: Cap all scores at 10
    education_score = min(education_score, 10)
    experience_score = min(experience_score, 10)  
    skills_score = min(skills_score, 10)
    match_score = min(match_score, 10)
    achievements_score = min(achievements_score, 10)
    
    # Calculate overall score (weighted) and cap at 10
    overall = (education_score * 0.2 + experience_score * 0.25 + 
               skills_score * 0.3 + match_score * 0.2 + achievements_score * 0.05)
    overall = min(overall, 10)  # CRITICAL: Cap overall at 10
    
    # Decision logic
    if overall >= 8.5:
        decision = "STRONG HIRE"
        recommendation = "Excellent fit! Top-tier candidate with matching skills and experience."
    elif overall >= 7.0:
        decision = "HIRE"
        recommendation = "Good fit with strong qualifications. Recommended for offer."
    elif overall >= 5.5:
        decision = "MAYBE"
        recommendation = "Decent fit but needs more evaluation. Consider for interview."
    elif overall >= 4.0:
        decision = "WEAK MAYBE"
        recommendation = "Some relevant experience but gaps in key areas."
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
        "achievements_score": round(achievements_score, 1),
        "hire_decision": decision,
        "recommendation": recommendation,
        "processing_time": round(processing_time, 3),
        "resume_skills": list(set(resume_skills)),
        "job_skills": list(set(job_skills)),
        "resume_length": len(resume_text),
        "job_length": len(job_description)
    }
123:@app.get("/", response_class=HTMLResponse)
124-def get_home():
125-    return """
126-    <!DOCTYPE html>
127-    <html>
128-    <head>
129-        <title>🚀 FitScore - AI Candidate Evaluation</title>
130-        <meta name="viewport" content="width=device-width, initial-scale=1.0">
131-        <style>
132-            * { margin: 0; padding: 0; box-sizing: border-box; }
133-            body { 
134-                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
135-                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
136-                min-height: 100vh; padding: 20px;
137-            }
138-            .container { 
139-                max-width: 1000px; margin: 0 auto; background: white;
140-                border-radius: 20px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
141-            }
142-            .header { text-align: center; margin-bottom: 40px; }
143-            .header h1 { color: #4f46e5; font-size: 3rem; margin-bottom: 10px; }
144-            .header p { color: #6b7280; font-size: 1.2rem; }
145-            .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }
146-            .form-group { margin-bottom: 25px; }
147-            label { display: block; margin-bottom: 8px; font-weight: 600; color: #374151; font-size: 1.1rem; }
148-            textarea { 
149-                width: 100%; padding: 15px; border: 2px solid #e5e7eb; 
150-                border-radius: 12px; font-size: 14px; min-height: 200px; resize: vertical;
151-            }
152-            .file-upload {
153-                width: 100%; padding: 20px; border: 2px dashed #e5e7eb;
154-                border-radius: 12px; text-align: center; cursor: pointer; transition: all 0.3s ease;
155-            }
156-            .file-upload:hover { border-color: #4f46e5; background: #f8fafc; }
157-            .file-upload input { display: none; }
158-            .analyze-btn {
159-                width: 100%; padding: 18px; background: #4f46e5; color: white;
160-                border: none; border-radius: 12px; font-size: 1.2rem; cursor: pointer;
161-                font-weight: 600; transition: all 0.3s ease;
162-            }
163-            .analyze-btn:hover { background: #4338ca; transform: translateY(-2px); }
164-            .result { margin-top: 40px; padding: 30px; background: #f8fafc; border-radius: 12px; }
165-            .score-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
166-            .score-card { 
167-                background: white; padding: 15px; border-radius: 12px; text-align: center;
168-                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
169-            }
170-            .score-value { font-size: 1.5rem; font-weight: bold; margin-bottom: 5px; }
171-            .score-label { color: #6b7280; font-size: 0.85rem; }
172-            .decision { font-size: 1.8rem; font-weight: bold; text-align: center; margin: 20px 0; padding: 20px; border-radius: 12px; }
173-            .strong-hire { background: #dcfce7; color: #166534; }
174-            .hire { background: #dbeafe; color: #1d4ed8; }
175-            .maybe { background: #fef3c7; color: #92400e; }
176-            .no-hire { background: #fecaca; color: #b91c1c; }
177-            .recommendation { background: white; padding: 20px; border-radius: 12px; margin: 20px 0; }
178-            .skills { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
179-            .skill-tag { background: #4f46e5; color: white; padding: 4px 10px; border-radius: 15px; font-size: 0.8rem; }
180-            @media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
181-        </style>
182-    </head>
183-    <body>
184-        <div class="container">
185-            <div class="header">
186-                <h1>🚀 FitScore</h1>
187-                <p>AI-Powered Job-to-Candidate Fit Analysis</p>
188-            </div>
189-            
190-            <form id="fitScoreForm" enctype="multipart/form-data">
191-                <div class="form-grid">
192-                    <div class="form-group">
193-                        <label>📄 Job Description</label>
194-                        <textarea id="jobDescription" placeholder="Paste the complete job description here..." required></textarea>
195-                    </div>
196-                    
197-                    <div class="form-group">
198-                        <label>📋 Resume Upload (PDF)</label>
199-                        <div class="file-upload" onclick="document.getElementById('resumeFile').click()">
200-                            <input type="file" id="resumeFile" accept=".pdf" required>
201-                            <div id="uploadText">
202-                                <p style="font-size: 1.1rem; margin-bottom: 10px;">📁 Click to upload PDF resume</p>
203-                                <p style="color: #6b7280; font-size: 0.9rem;">PDF files only</p>
204-                            </div>
205-                        </div>
206-                    </div>
207-                </div>
208-                
209-                <button type="submit" class="analyze-btn" id="analyzeBtn">
210-                    🔍 Analyze Job-Candidate Fit
211-                </button>
212-            </form>
213-            
214-            <div id="result" class="result" style="display: none;"></div>
215-        </div>
216-
217-        <script>
218-            document.getElementById('resumeFile').addEventListener('change', function(e) {
219-                const file = e.target.files[0];
220-                if (file) {
221-                    document.getElementById('uploadText').innerHTML = 
222-                        '<p style="color: #4f46e5; font-weight: 600;">✅ ' + file.name + '</p>' +
223-                        '<p style="color: #6b7280; font-size: 0.9rem;">Ready to analyze</p>';
224-                }
225-            });
226-
227-            document.getElementById('fitScoreForm').addEventListener('submit', async (e) => {
228-                e.preventDefault();
229-                
230-                const jobDesc = document.getElementById('jobDescription').value.trim();
231-                const resumeFile = document.getElementById('resumeFile').files[0];
232-                
233-                if (!jobDesc || !resumeFile) {
234-                    alert('Please provide both job description and resume file');
235-                    return;
236-                }
237-                
238-                const analyzeBtn = document.getElementById('analyzeBtn');
239-                analyzeBtn.innerHTML = '⏳ Analyzing...';
240-                analyzeBtn.disabled = true;
241-                
242-                const formData = new FormData();
243-                formData.append('job_description', jobDesc);
244-                formData.append('resume_file', resumeFile);
245-                
246-                try {
247-                    const response = await fetch('/analyze-fit', {
248-                        method: 'POST',
249-                        body: formData
250-                    });
251-                    
252-                    const result = await response.json();
253-                    
254-                    if (response.ok) {
255-                        displayResult(result);
256-                    } else {
257-                        throw new Error(result.detail || 'Analysis failed');
258-                    }
259-                } catch (error) {
260-                    document.getElementById('result').innerHTML = 
261-                        '<div style="color: #ef4444; text-align: center; padding: 20px;"><h3>❌ Analysis Failed</h3><p>' + error.message + '</p></div>';
262-                    document.getElementById('result').style.display = 'block';
263-                } finally {
264-                    analyzeBtn.innerHTML = '🔍 Analyze Job-Candidate Fit';
265-                    analyzeBtn.disabled = false;
266-                }
267-            });
268-            
269-            function displayResult(result) {
270-                const decisionClass = result.hire_decision.toLowerCase().replace(/[^a-z]/g, '-');
271-                
272-                const html = \`
273-                    <div class="decision \${decisionClass}">
274-                        \${result.hire_decision}: \${result.overall_score}/10
275-                    </div>
276-                    
277-                    <div class="recommendation">
278-                        <h3 style="margin-bottom: 10px;">💡 Recommendation</h3>
279-                        <p>\${result.recommendation}</p>
280-                    </div>
281-                    
282-                    <div class="score-grid">
283-                        <div class="score-card">
284-                            <div class="score-value" style="color: #7c3aed;">\${result.education_score}</div>
285-                            <div class="score-label">Education</div>
286-                        </div>
287-                        <div class="score-card">
288-                            <div class="score-value" style="color: #2563eb;">\${result.experience_score}</div>
289-                            <div class="score-label">Experience</div>
290-                        </div>
291-                        <div class="score-card">
292-                            <div class="score-value" style="color: #dc2626;">\${result.skills_score}</div>
293-                            <div class="score-label">Skills</div>
294-                        </div>
295-                        <div class="score-card">
296-                            <div class="score-value" style="color: #16a34a;">\${result.match_score}</div>
297-                            <div class="score-label">Job Match</div>
298-                        </div>
299-                    </div>
300-                    
301-                    <div style="background: white; padding: 20px; border-radius: 12px; margin: 20px 0;">
302-                        <h3 style="margin-bottom: 15px;">🎯 Resume Skills Found</h3>
303-                        <div class="skills">
304-                            \${result.resume_skills.map(skill => \`<span class="skill-tag">\${skill}</span>\`).join('')}
305-                        </div>
306-                    </div>
307-                    
308-                    <div style="text-align: center; color: #6b7280; margin-top: 20px;">
309-                        <p>⚡ Processed in \${result.processing_time}s</p>
310-                    </div>
311-                \`;
312-                
313-                document.getElementById('result').innerHTML = html;
314-                document.getElementById('result').style.display = 'block';
315-            }
316-        </script>
317-    </body>
318-    </html>
319-    """
320-
321-@app.post("/analyze-fit")
322-async def analyze_job_fit(
323-    job_description: str = Form(...),
324-    resume_file: UploadFile = File(...)
325-):
326-    """Analyze fit between job description and resume PDF"""
327-    try:
328-        # Validate inputs
329-        if not job_description or len(job_description.strip()) < 50:
330-            raise HTTPException(status_code=400, detail="Job description must be at least 50 characters")
331-        
332-        if not resume_file.filename.lower().endswith('.pdf'):
333-            raise HTTPException(status_code=400, detail="Resume must be a PDF file")
334-        
335-        # Extract text from PDF
336-        pdf_bytes = await resume_file.read()
337-        resume_text = extract_pdf_text(pdf_bytes)
338-        
339-        if len(resume_text.strip()) < 50:
340-            raise HTTPException(status_code=400, detail="Could not extract sufficient text from PDF")
341-        
342-        # Calculate fit score
343-        result = calculate_fit_score(resume_text, job_description)
344-        
345-        return result
346-        
347-    except HTTPException:
348-        raise
349-    except Exception as e:
350-        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
351-
352:@app.get("/health")
353-def health_check():
354-    return {"status": "healthy", "service": "fitscore-complete", "version": "2.0.0"}
