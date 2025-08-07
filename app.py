#!/usr/bin/env python3
"""
Simplified FitScore Test App for Vercel
Self-contained version with embedded optimized scoring
"""

import os
import sys
import time
import json
import asyncio
import re
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import hashlib

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import fitz  # PyMuPDF for PDF processing
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall": self.overall,
            "education": self.education,
            "experience": self.experience,
            "skills": self.skills,
            "achievements": self.achievements,
            "confidence": self.confidence,
            "hire_decision": self.hire_decision,
            "strengths": self.strengths,
            "concerns": self.concerns,
            "processing_time": self.processing_time
        }

class FastEliteTalentDetector:
    """Simplified elite talent detection for Vercel"""
    
    def __init__(self):
        # Elite universities with scores
        self.elite_unis = {
            r"\b(MIT|Stanford|Harvard|Berkeley|UC Berkeley|Caltech|Princeton|Yale|Columbia|UPenn|Cornell)\b": 9.5,
            r"\b(Waterloo|Georgia Tech|CMU|Carnegie Mellon|UIUC|UT Austin|University of Washington|UW)\b": 9.2,
            r"\b(Oxford|Cambridge|ETH|IIT|Indian Institute of Technology|Tsinghua|Peking University)\b": 9.0,
            r"\b(UCLA|USC|Michigan|Northwestern|Duke|University of Chicago)\b": 7.8,
            r"\b(UCSD|UC San Diego|Wisconsin|Virginia|UVA|North Carolina|UNC)\b": 6.5
        }
        
        # Elite companies with scores
        self.elite_companies = {
            r"\b(Google|Meta|Facebook|Apple|Netflix|Amazon|Microsoft)\b": 9.5,
            r"\b(Stripe|Scale AI|Databricks|Figma|Notion|Linear|OpenAI|Anthropic|Airbnb|Uber)\b": 9.2,
            r"\b(Coinbase|Snowflake|Palantir|Slack|Zoom|Dropbox|Twilio|GitLab)\b": 8.7,
            r"\b(McKinsey|Bain|BCG|Boston Consulting|Deloitte Consulting)\b": 8.5,
            r"\b(Goldman Sachs|Morgan Stanley|JP Morgan|JPMorgan|Blackstone|KKR|Citadel)\b": 8.3
        }
        
        # Achievement patterns
        self.achievements = {
            r"\b(patent|published|publication|TED talk|keynote|conference speaker|open source|GitHub|acquisition|IPO|Forbes|YC|Y Combinator|founder|co-founder)\b": 9.0,
            r"\b(award|recognition|promotion|mentored|scaled|optimized|launched|increased \d+%|reduced \d+%|grew \d+%|saved \$|revenue \$)\b": 7.5,
            r"\b(improved|enhanced|developed|built|created|designed|implemented)\b": 6.0
        }
        
        # Technical skills for software engineers
        self.tech_skills = {
            r"\b(Python|Java|JavaScript|TypeScript|Go|Rust|C\+\+|React|Node\.js|Django|Flask|Spring|Kubernetes|Docker|AWS|GCP|Azure)\b": 2.0,
            r"\b(system design|microservices|distributed systems|scalability|performance optimization|machine learning|AI|blockchain)\b": 3.0,
            r"\b(architecture|technical leadership|code review|mentoring|hiring|team building)\b": 2.5
        }
    
    def detect_pattern_score(self, text: str, patterns: Dict[str, float]) -> Tuple[float, List[str]]:
        """Detect patterns and return max score + matches"""
        max_score = 0.0
        matches = []
        
        for pattern, score in patterns.items():
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                max_score = max(max_score, score)
                matches.extend(found)
        
        return max_score, matches
    
    def evaluate_candidate(self, text: str, role: str = "software_engineer") -> EliteScore:
        """Fast candidate evaluation"""
        start_time = time.time()
        
        # Education scoring
        edu_score, edu_matches = self.detect_pattern_score(text, self.elite_unis)
        if not edu_matches and re.search(r"\b(degree|bachelor|master|phd|bs|ms|mba)\b", text, re.IGNORECASE):
            edu_score = 5.0
            edu_matches = ["General degree"]
        
        # Experience scoring
        exp_score, exp_matches = self.detect_pattern_score(text, self.elite_companies)
        # Years bonus
        years_pattern = re.findall(r"(\d+)\+?\s*years?\s+(of\s+)?experience", text, re.IGNORECASE)
        if years_pattern:
            years = max([int(year[0]) for year in years_pattern])
            if years >= 10:
                exp_score += 1.0
            elif years >= 5:
                exp_score += 0.5
        
        if not exp_matches and re.search(r"\b(engineer|developer|manager|analyst|consultant)\b", text, re.IGNORECASE):
            exp_score = max(exp_score, 5.0)
            exp_matches = ["General experience"]
        
        # Skills scoring
        skills_score = 0
        skills_matches = []
        for pattern, score in self.tech_skills.items():
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                skills_score += min(len(set(found)) * score, score * 2)
                skills_matches.extend(found)
        skills_score = min(skills_score, 10.0)
        
        # Achievements scoring
        ach_score = 0
        ach_matches = []
        for pattern, score in self.achievements.items():
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                ach_score += min(len(found) * (score/3), score)
                ach_matches.extend(found)
        ach_score = min(ach_score, 10.0)
        
        # Role-specific weights
        if role == "software_engineer":
            weights = {"education": 0.15, "experience": 0.35, "skills": 0.25, "achievements": 0.25}
            hire_threshold = 7.5
        elif role == "product_manager":
            weights = {"education": 0.10, "experience": 0.40, "skills": 0.30, "achievements": 0.20}
            hire_threshold = 7.0
        else:  # data_scientist
            weights = {"education": 0.20, "experience": 0.30, "skills": 0.35, "achievements": 0.15}
            hire_threshold = 7.2
        
        # Calculate overall score
        overall = (
            edu_score * weights["education"] +
            exp_score * weights["experience"] +
            skills_score * weights["skills"] +
            ach_score * weights["achievements"]
        )
        
        # Determine hire decision
        if overall >= 8.5:
            decision = "HIRE"
        elif overall >= hire_threshold:
            decision = "STRONG_MAYBE"
        elif overall >= 6.0:
            decision = "MAYBE"
        else:
            decision = "NO_HIRE"
        
        # Generate strengths and concerns
        strengths = []
        concerns = []
        
        if edu_score >= 8.0:
            strengths.append(f"Elite education: {', '.join(edu_matches[:2])}")
        elif edu_score < 6.0:
            concerns.append("Education background below expectations")
        
        if exp_score >= 8.0:
            strengths.append(f"Top-tier experience: {', '.join(exp_matches[:2])}")
        elif exp_score < 6.0:
            concerns.append("Limited relevant experience")
        
        if skills_score >= 8.0:
            strengths.append(f"Strong technical skills: {', '.join(skills_matches[:3])}")
        elif skills_score < 6.0:
            concerns.append("Missing key technical skills")
        
        if ach_score >= 7.0:
            strengths.append(f"Notable achievements: {', '.join(ach_matches[:2])}")
        elif ach_score < 4.0:
            concerns.append("Limited demonstrated impact")
        
        # Calculate confidence
        confidence = min(95.0, 60.0 + (len(text) / 100) + (len(edu_matches + exp_matches + skills_matches) * 5))
        
        processing_time = time.time() - start_time
        
        return EliteScore(
            overall=round(overall, 1),
            education=round(edu_score, 1),
            experience=round(exp_score, 1),
            skills=round(skills_score, 1),
            achievements=round(ach_score, 1),
            confidence=round(confidence, 1),
            hire_decision=decision,
            strengths=strengths[:3],
            concerns=concerns[:2],
            processing_time=round(processing_time, 3)
        )

# Initialize FastAPI app
app = FastAPI(
    title="Fast FitScore Test App",
    description="Simplified FitScore testing - 10x faster elite talent detection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detector
detector = FastEliteTalentDetector()

async def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes"""
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text if text.strip() else "Could not extract text from PDF"
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
        <title>Fast FitScore Test App</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }
            .container {
                max-width: 1200px; margin: 0 auto; background: white;
                border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white; padding: 30px; text-align: center;
            }
            .header h1 { font-size: 2.5rem; margin-bottom: 10px; font-weight: 700; }
            .header p { font-size: 1.1rem; opacity: 0.9; }
            .content { display: grid; grid-template-columns: 1fr 1fr; gap: 0; min-height: 600px; }
            .input-section { padding: 40px; border-right: 1px solid #e5e7eb; }
            .result-section { padding: 40px; background: #f8fafc; }
            .form-group { margin-bottom: 25px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; color: #374151; }
            textarea, select {
                width: 100%; padding: 15px; border: 2px solid #e5e7eb; border-radius: 12px;
                font-size: 14px; font-family: inherit; transition: all 0.2s;
            }
            textarea:focus, select:focus {
                outline: none; border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
            }
            .file-upload {
                border: 2px dashed #d1d5db; border-radius: 12px; padding: 30px;
                text-align: center; transition: all 0.2s; cursor: pointer;
            }
            .file-upload:hover { border-color: #4f46e5; background: #f8fafc; }
            input[type="file"] { display: none; }
            .analyze-btn {
                width: 100%; padding: 15px 30px;
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white; border: none; border-radius: 12px;
                font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
            }
            .analyze-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3); }
            .loading { display: none; text-align: center; padding: 40px; }
            .spinner {
                border: 4px solid #f3f4f6; border-top: 4px solid #4f46e5; border-radius: 50%;
                width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px;
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .result-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
            .score-display { text-align: center; margin-bottom: 25px; }
            .overall-score { font-size: 3rem; font-weight: 700; margin-bottom: 10px; }
            .score-excellent { color: #10b981; } .score-good { color: #3b82f6; }
            .score-fair { color: #f59e0b; } .score-poor { color: #ef4444; }
            .hire-decision { font-size: 1.2rem; font-weight: 600; padding: 8px 16px; border-radius: 20px; display: inline-block; }
            .hire-decision.hire { background: #d1fae5; color: #065f46; }
            .hire-decision.strong-maybe { background: #dbeafe; color: #1e40af; }
            .hire-decision.maybe { background: #fef3c7; color: #92400e; }
            .hire-decision.no-hire { background: #fecaca; color: #991b1b; }
            @media (max-width: 768px) { .content { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Fast FitScore Test App</h1>
                <p>Ultra-fast AI-powered candidate evaluation • 10x faster results</p>
            </div>
            
            <div class="content">
                <div class="input-section">
                    <form id="fitscoreForm">
                        <div class="form-group">
                            <label for="jobDescription">Job Description</label>
                            <textarea id="jobDescription" rows="8" placeholder="Paste the job description here..." required></textarea>
                        </div>
                        
                        <div class="form-group">
                            <label for="role">Role Type</label>
                            <select id="role">
                                <option value="software_engineer">Software Engineer</option>
                                <option value="product_manager">Product Manager</option>
                                <option value="data_scientist">Data Scientist</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>Resume Upload</label>
                            <div class="file-upload" onclick="document.getElementById('resumeFile').click()">
                                <div style="font-size: 2rem; margin-bottom: 10px;">📄</div>
                                <div>Click to upload PDF resume or drag & drop</div>
                                <small>Supports PDF files up to 10MB</small>
                            </div>
                            <input type="file" id="resumeFile" accept=".pdf" />
                        </div>
                        
                        <button type="submit" class="analyze-btn">🧠 Analyze Candidate</button>
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
            const fileInput = document.getElementById('resumeFile');
            const fileUpload = document.querySelector('.file-upload');
            
            fileInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    fileUpload.innerHTML = '<div style="font-size: 2rem; margin-bottom: 10px;">✅</div><div>File uploaded: ' + this.files[0].name + '</div><small>Click to change file</small>';
                }
            });
            
            document.getElementById('fitscoreForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData();
                const jobDescription = document.getElementById('jobDescription').value;
                const role = document.getElementById('role').value;
                const resumeFile = document.getElementById('resumeFile').files[0];
                
                if (!jobDescription.trim()) { alert('Please enter a job description'); return; }
                if (!resumeFile) { alert('Please upload a resume PDF'); return; }
                
                formData.append('job_description', jobDescription);
                formData.append('role_type', role);
                formData.append('resume', resumeFile);
                
                document.getElementById('resultContent').style.display = 'none';
                document.getElementById('loading').style.display = 'block';
                
                try {
                    const response = await fetch('/analyze', { method: 'POST', body: formData });
                    const result = await response.json();
                    
                    if (response.ok) {
                        displayResults(result);
                    } else {
                        throw new Error(result.detail || 'Analysis failed');
                    }
                } catch (error) {
                    document.getElementById('resultContent').innerHTML = '<div class="result-card"><div style="text-align: center; color: #dc2626;"><h3>❌ Analysis Failed</h3><p>' + error.message + '</p></div></div>';
                } finally {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('resultContent').style.display = 'block';
                }
            });
            
            function displayResults(result) {
                const score = result.evaluation;
                let scoreClass = 'score-poor';
                if (score.overall >= 8.5) scoreClass = 'score-excellent';
                else if (score.overall >= 7.0) scoreClass = 'score-good';
                else if (score.overall >= 6.0) scoreClass = 'score-fair';
                
                let decisionClass = 'no-hire';
                if (score.hire_decision === 'HIRE') decisionClass = 'hire';
                else if (score.hire_decision === 'STRONG_MAYBE') decisionClass = 'strong-maybe';
                else if (score.hire_decision === 'MAYBE') decisionClass = 'maybe';
                
                const html = '<div class="result-card"><div class="score-display"><div class="overall-score ' + scoreClass + '">' + score.overall + '/10</div><div class="hire-decision ' + decisionClass + '">' + score.hire_decision.replace('_', ' ') + '</div></div><div style="margin: 20px 0;"><strong>Processing Time:</strong> ' + score.processing_time + 's</div><div style="margin: 20px 0;"><strong>Confidence:</strong> ' + score.confidence + '%</div>' + (score.strengths.length > 0 ? '<div style="margin: 20px 0;"><strong>💪 Strengths:</strong><ul>' + score.strengths.map(s => '<li>' + s + '</li>').join('') + '</ul></div>' : '') + (score.concerns.length > 0 ? '<div style="margin: 20px 0;"><strong>⚠️ Concerns:</strong><ul>' + score.concerns.map(c => '<li>' + c + '</li>').join('') + '</ul></div>' : '') + '</div>';
                
                document.getElementById('resultContent').innerHTML = html;
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/analyze")
async def analyze_candidate(
    job_description: str = Form(...),
    role_type: str = Form("software_engineer"),
    resume: UploadFile = File(...)
):
    """Analyze candidate using simplified fast evaluation"""
    start_time = time.time()
    
    try:
        if not resume.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        pdf_bytes = await resume.read()
        resume_text = await extract_pdf_text(pdf_bytes)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract meaningful text from PDF")
        
        # Run fast evaluation
        elite_score = detector.evaluate_candidate(resume_text, role_type)
        
        return {
            "evaluation": elite_score.to_dict(),
            "processing_time": round(time.time() - start_time, 2),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fast-fitscore-app", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 