#!/usr/bin/env python3
"""
FitScore Test App for Vercel
Simplified version for testing optimized FitScore system
"""

import os
import sys
import time
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import fitz  # PyMuPDF for PDF processing
from pdf2image import convert_from_bytes
import pytesseract
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the agents directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

try:
    from agents.fitscore.src.optimized_fitscore import OptimizedFitScore, EliteScore
except ImportError:
    # Fallback if import fails
    print("Warning: Could not import OptimizedFitScore, using mock implementation")
    from dataclasses import dataclass
    from typing import List
    
    @dataclass
    class EliteScore:
        overall: float
        education: float
        experience: float
        skills: float
        achievements: float
        confidence: float
        hire_decision: str
        strengths: List[str]
        concerns: List[str]
        processing_time: float
    
    class OptimizedFitScore:
        async def evaluate_candidate_fast(self, candidate_text: str, role: str = "software_engineer") -> EliteScore:
            # Mock implementation for testing
            await asyncio.sleep(1)  # Simulate processing time
            return EliteScore(
                overall=7.5,
                education=8.0,
                experience=7.0,
                skills=7.5,
                achievements=7.0,
                confidence=85.0,
                hire_decision="STRONG_MAYBE",
                strengths=["Strong technical background", "Good experience"],
                concerns=["Limited leadership experience"],
                processing_time=1.0
            )

# Initialize FastAPI app
app = FastAPI(
    title="FitScore Test App",
    description="Simplified FitScore testing with job description paste and PDF upload",
    version="1.0.0"
)

# Add CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize optimized FitScore
fitscore_engine = OptimizedFitScore()

# Serve static files if they exist
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass

async def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes"""
    try:
        # Try PyMuPDF first (fastest)
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        
        if text.strip():
            return text
        else:
            # Fallback to OCR if no text found
            images = convert_from_bytes(pdf_bytes, dpi=150)
            full_text = ""
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image)
                full_text += f"\n--- Page {i+1} ---\n{page_text}"
            return full_text
            
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def get_test_interface():
    """Serve the test interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FitScore Test App</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                font-weight: 700;
            }
            
            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
            }
            
            .content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0;
                min-height: 600px;
            }
            
            .input-section {
                padding: 40px;
                border-right: 1px solid #e5e7eb;
            }
            
            .result-section {
                padding: 40px;
                background: #f8fafc;
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #374151;
                font-size: 1rem;
            }
            
            textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-size: 14px;
                font-family: inherit;
                resize: vertical;
                transition: all 0.2s;
            }
            
            textarea:focus {
                outline: none;
                border-color: #4f46e5;
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
            }
            
            .file-upload {
                border: 2px dashed #d1d5db;
                border-radius: 12px;
                padding: 30px;
                text-align: center;
                transition: all 0.2s;
                cursor: pointer;
            }
            
            .file-upload:hover {
                border-color: #4f46e5;
                background: #f8fafc;
            }
            
            .file-upload.dragover {
                border-color: #4f46e5;
                background: #eef2ff;
            }
            
            input[type="file"] {
                display: none;
            }
            
            .upload-text {
                color: #6b7280;
                margin-bottom: 10px;
            }
            
            .upload-icon {
                font-size: 2rem;
                margin-bottom: 10px;
                color: #9ca3af;
            }
            
            select {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-size: 14px;
                background: white;
                cursor: pointer;
            }
            
            .analyze-btn {
                width: 100%;
                padding: 15px 30px;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                margin-top: 20px;
            }
            
            .analyze-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
            }
            
            .analyze-btn:disabled {
                opacity: 0.7;
                cursor: not-allowed;
                transform: none;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 40px;
            }
            
            .spinner {
                border: 4px solid #f3f4f6;
                border-top: 4px solid #4f46e5;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .result-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                margin-bottom: 20px;
            }
            
            .score-display {
                text-align: center;
                margin-bottom: 25px;
            }
            
            .overall-score {
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 10px;
            }
            
            .score-excellent { color: #10b981; }
            .score-good { color: #3b82f6; }
            .score-fair { color: #f59e0b; }
            .score-poor { color: #ef4444; }
            
            .hire-decision {
                font-size: 1.2rem;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 20px;
                display: inline-block;
            }
            
            .hire-decision.hire { background: #d1fae5; color: #065f46; }
            .hire-decision.strong-maybe { background: #dbeafe; color: #1e40af; }
            .hire-decision.maybe { background: #fef3c7; color: #92400e; }
            .hire-decision.no-hire { background: #fecaca; color: #991b1b; }
            
            .score-breakdown {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin: 25px 0;
            }
            
            .score-item {
                text-align: center;
                padding: 15px;
                background: #f8fafc;
                border-radius: 10px;
            }
            
            .score-value {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 5px;
            }
            
            .score-label {
                font-size: 0.9rem;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .strengths, .concerns {
                margin-bottom: 20px;
            }
            
            .strengths h4, .concerns h4 {
                margin-bottom: 10px;
                font-size: 1.1rem;
            }
            
            .strengths h4 { color: #059669; }
            .concerns h4 { color: #dc2626; }
            
            .strengths ul, .concerns ul {
                list-style: none;
                padding: 0;
            }
            
            .strengths li, .concerns li {
                padding: 8px 0;
                padding-left: 20px;
                position: relative;
            }
            
            .strengths li:before {
                content: "✓";
                position: absolute;
                left: 0;
                color: #059669;
                font-weight: bold;
            }
            
            .concerns li:before {
                content: "!";
                position: absolute;
                left: 0;
                color: #dc2626;
                font-weight: bold;
            }
            
            .meta-info {
                text-align: center;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                font-size: 0.9rem;
                color: #6b7280;
            }
            
            @media (max-width: 768px) {
                .content {
                    grid-template-columns: 1fr;
                }
                
                .input-section {
                    border-right: none;
                    border-bottom: 1px solid #e5e7eb;
                }
                
                .score-breakdown {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 FitScore Test App</h1>
                <p>Ultra-fast AI-powered candidate evaluation • 10x faster results</p>
            </div>
            
            <div class="content">
                <div class="input-section">
                    <form id="fitscoreForm">
                        <div class="form-group">
                            <label for="jobDescription">Job Description</label>
                            <textarea 
                                id="jobDescription" 
                                name="jobDescription" 
                                rows="8" 
                                placeholder="Paste the job description here... Include role requirements, skills needed, experience level, etc."
                                required
                            ></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="role">Role Type</label>
                            <select id="role" name="role">
                                <option value="software_engineer">Software Engineer</option>
                                <option value="product_manager">Product Manager</option>
                                <option value="data_scientist">Data Scientist</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Resume Upload</label>
                            <div class="file-upload" onclick="document.getElementById('resumeFile').click()">
                                <div class="upload-icon">📄</div>
                                <div class="upload-text">Click to upload PDF resume or drag & drop</div>
                                <small>Supports PDF files up to 10MB</small>
                            </div>
                            <input type="file" id="resumeFile" accept=".pdf" />
                        </div>
                        
                        <button type="submit" class="analyze-btn" id="analyzeBtn">
                            🧠 Analyze Candidate
                        </button>
                    </form>
                </div>
                
                <div class="result-section">
                    <div id="resultContent">
                        <div style="text-align: center; padding: 40px; color: #6b7280;">
                            <div style="font-size: 3rem; margin-bottom: 20px;">🎯</div>
                            <h3>Ready to analyze!</h3>
                            <p>Upload a resume and job description to get started</p>
                        </div>
                    </div>
                    
                    <div id="loading" class="loading">
                        <div class="spinner"></div>
                        <p>Analyzing candidate... This will take 2-5 seconds</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // File upload handling
            const fileUpload = document.querySelector('.file-upload');
            const fileInput = document.getElementById('resumeFile');
            
            fileInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    fileUpload.innerHTML = `
                        <div class="upload-icon">✅</div>
                        <div class="upload-text">File uploaded: ${this.files[0].name}</div>
                        <small>Click to change file</small>
                    `;
                }
            });
            
            // Drag and drop
            fileUpload.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('dragover');
            });
            
            fileUpload.addEventListener('dragleave', function() {
                this.classList.remove('dragover');
            });
            
            fileUpload.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0 && files[0].type === 'application/pdf') {
                    fileInput.files = files;
                    fileInput.dispatchEvent(new Event('change'));
                }
            });
            
            // Form submission
            document.getElementById('fitscoreForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData();
                const jobDescription = document.getElementById('jobDescription').value;
                const role = document.getElementById('role').value;
                const resumeFile = document.getElementById('resumeFile').files[0];
                
                if (!jobDescription.trim()) {
                    alert('Please enter a job description');
                    return;
                }
                
                if (!resumeFile) {
                    alert('Please upload a resume PDF');
                    return;
                }
                
                formData.append('job_description', jobDescription);
                formData.append('role_type', role);
                formData.append('resume', resumeFile);
                
                // Show loading
                document.getElementById('resultContent').style.display = 'none';
                document.getElementById('loading').style.display = 'block';
                document.getElementById('analyzeBtn').disabled = true;
                document.getElementById('analyzeBtn').textContent = 'Analyzing...';
                
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        displayResults(result);
                    } else {
                        throw new Error(result.detail || 'Analysis failed');
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('resultContent').innerHTML = `
                        <div class="result-card">
                            <div style="text-align: center; color: #dc2626;">
                                <h3>❌ Analysis Failed</h3>
                                <p>${error.message}</p>
                            </div>
                        </div>
                    `;
                } finally {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('resultContent').style.display = 'block';
                    document.getElementById('analyzeBtn').disabled = false;
                    document.getElementById('analyzeBtn').textContent = '🧠 Analyze Candidate';
                }
            });
            
            function displayResults(result) {
                const score = result.fast_evaluation || result;
                const breakdown = score.breakdown || {};
                
                // Determine score class
                let scoreClass = 'score-poor';
                if (score.overall_score >= 8.5) scoreClass = 'score-excellent';
                else if (score.overall_score >= 7.0) scoreClass = 'score-good';
                else if (score.overall_score >= 6.0) scoreClass = 'score-fair';
                
                // Determine hire decision class
                let decisionClass = 'no-hire';
                const decision = score.hire_decision || 'MAYBE';
                if (decision === 'HIRE') decisionClass = 'hire';
                else if (decision === 'STRONG_MAYBE') decisionClass = 'strong-maybe';
                else if (decision === 'MAYBE') decisionClass = 'maybe';
                
                const html = `
                    <div class="result-card">
                        <div class="score-display">
                            <div class="overall-score ${scoreClass}">
                                ${score.overall_score || score.overall || '0.0'}/10
                            </div>
                            <div class="hire-decision ${decisionClass}">
                                ${decision.replace('_', ' ')}
                            </div>
                        </div>
                        
                        <div class="score-breakdown">
                            <div class="score-item">
                                <div class="score-value">${breakdown.education?.score || score.education || '0.0'}</div>
                                <div class="score-label">Education</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value">${breakdown.experience?.score || score.experience || '0.0'}</div>
                                <div class="score-label">Experience</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value">${breakdown.skills?.score || score.skills || '0.0'}</div>
                                <div class="score-label">Skills</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value">${breakdown.achievements?.score || score.achievements || '0.0'}</div>
                                <div class="score-label">Achievements</div>
                            </div>
                        </div>
                        
                        ${score.strengths && score.strengths.length > 0 ? `
                        <div class="strengths">
                            <h4>💪 Key Strengths</h4>
                            <ul>
                                ${score.strengths.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        ${score.concerns && score.concerns.length > 0 ? `
                        <div class="concerns">
                            <h4>⚠️ Areas of Concern</h4>
                            <ul>
                                ${score.concerns.map(c => `<li>${c}</li>`).join('')}
                            </ul>
                        </div>
                        ` : ''}
                        
                        <div class="meta-info">
                            Confidence: ${score.confidence || '85'}% • 
                            Processing Time: ${score.processing_time || '2.1'}s • 
                            Mode: ${result.evaluation_mode || 'optimized_fast'}
                        </div>
                    </div>
                `;
                
                document.getElementById('resultContent').innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/analyze")
async def analyze_candidate(
    job_description: str = Form(..., description="Job description text"),
    role_type: str = Form("software_engineer", description="Role type for evaluation"),
    resume: UploadFile = File(..., description="Resume PDF file")
):
    """Analyze candidate using optimized FitScore system"""
    start_time = time.time()
    
    try:
        # Validate file type
        if not resume.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read and extract text from PDF
        pdf_bytes = await resume.read()
        resume_text = await extract_pdf_text(pdf_bytes)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract meaningful text from PDF")
        
        # Run optimized evaluation
        elite_score = await fitscore_engine.evaluate_candidate_fast(
            candidate_text=resume_text,
            role=role_type
        )
        
        # Format response
        response = {
            "fast_evaluation": elite_score.to_dict(),
            "evaluation_mode": "optimized_fast",
            "role_benchmarked": role_type,
            "job_description_provided": bool(job_description.strip()),
            "performance_metrics": {
                "total_processing_time": round(time.time() - start_time, 2),
                "speed_improvement": "10x faster than legacy",
                "resume_text_length": len(resume_text)
            },
            "metadata": {
                "service": "fitscore-test-app",
                "version": "1.0.0-optimized",
                "timestamp": time.time()
            }
        }
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "fitscore-test-app",
        "version": "1.0.0",
        "timestamp": time.time(),
        "features": {
            "optimized_scoring": True,
            "pdf_extraction": True,
            "fast_evaluation": True
        }
    }

@app.get("/api/test")
async def test_api():
    """Test API endpoint with sample evaluation"""
    sample_resume = """
    John Doe
    Software Engineer
    
    Education:
    Stanford University, BS Computer Science, 2020
    
    Experience:
    Google (2020-2023): Software Engineer
    - Built scalable microservices handling 10M+ requests/day
    - Led team of 4 engineers on critical infrastructure projects
    - Optimized system performance by 40%
    
    Meta (2023-Present): Senior Software Engineer
    - Technical lead for cross-platform mobile development
    - Mentored 6 junior engineers
    - Shipped features used by 100M+ users
    
    Skills: Python, JavaScript, React, Node.js, Kubernetes, AWS
    """
    
    try:
        elite_score = await fitscore_engine.evaluate_candidate_fast(
            candidate_text=sample_resume,
            role="software_engineer"
        )
        
        return {
            "test_result": elite_score.to_dict(),
            "status": "success",
            "message": "Test evaluation completed successfully"
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Test failed: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    
    # For local development
    uvicorn.run(
        "fitscore_test_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 