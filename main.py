from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import re
import time
from typing import List

app = FastAPI()

# Simplified elite detection patterns
ELITE_PATTERNS = {
    "education": {
        r"\b(MIT|Stanford|Harvard|Berkeley|Caltech|Princeton|Yale)\b": 9.5,
        r"\b(Waterloo|Georgia Tech|CMU|Carnegie Mellon)\b": 9.0,
        r"\b(UCLA|USC|Michigan|Northwestern|Duke)\b": 7.5,
    },
    "companies": {
        r"\b(Google|Meta|Facebook|Apple|Netflix|Amazon|Microsoft)\b": 9.5,
        r"\b(Stripe|Airbnb|Uber|OpenAI|Anthropic)\b": 9.0,
        r"\b(McKinsey|Bain|BCG|Goldman Sachs)\b": 8.5,
    },
    "skills": {
        r"\b(Python|JavaScript|React|AWS|Kubernetes|Docker)\b": 2.0,
        r"\b(system design|machine learning|AI)\b": 3.0,
    }
}

def evaluate_text(text: str) -> dict:
    """Simple text-based evaluation"""
    start_time = time.time()
    
    scores = {"education": 0, "experience": 0, "skills": 0}
    matches = {"education": [], "experience": [], "skills": []}
    
    # Education scoring
    for pattern, score in ELITE_PATTERNS["education"].items():
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            scores["education"] = max(scores["education"], score)
            matches["education"].extend(found)
    
    # Experience scoring  
    for pattern, score in ELITE_PATTERNS["companies"].items():
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            scores["experience"] = max(scores["experience"], score)
            matches["experience"].extend(found)
    
    # Skills scoring
    for pattern, score in ELITE_PATTERNS["skills"].items():
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            scores["skills"] += min(len(found) * score, 10)
    
    # Overall calculation
    overall = (scores["education"] * 0.2 + scores["experience"] * 0.4 + scores["skills"] * 0.4)
    
    # Decision logic
    if overall >= 8.5:
        decision = "HIRE"
    elif overall >= 7.0:
        decision = "STRONG_MAYBE"
    elif overall >= 5.0:
        decision = "MAYBE"
    else:
        decision = "NO_HIRE"
    
    processing_time = time.time() - start_time
    
    return {
        "overall": round(overall, 1),
        "education": round(scores["education"], 1),
        "experience": round(scores["experience"], 1),
        "skills": round(scores["skills"], 1),
        "hire_decision": decision,
        "processing_time": round(processing_time, 3),
        "strengths": [f"Found: {', '.join(matches['education'][:2])}" if matches['education'] else ""],
        "concerns": ["Limited data" if not any(matches.values()) else ""]
    }

@app.get("/", response_class=HTMLResponse)
def get_home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fast FitScore Test</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }
            .container { 
                max-width: 800px; margin: 0 auto; background: white;
                border-radius: 20px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { color: #4f46e5; font-size: 2.5rem; margin-bottom: 10px; }
            .header p { color: #6b7280; font-size: 1.1rem; }
            .form-group { margin-bottom: 25px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; color: #374151; }
            textarea { 
                width: 100%; padding: 15px; border: 2px solid #e5e7eb; 
                border-radius: 12px; font-size: 14px; min-height: 200px;
            }
            .analyze-btn {
                width: 100%; padding: 15px; background: #4f46e5; color: white;
                border: none; border-radius: 12px; font-size: 1.1rem; cursor: pointer;
            }
            .analyze-btn:hover { background: #4338ca; }
            .result { margin-top: 30px; padding: 20px; background: #f8fafc; border-radius: 12px; }
            .score { font-size: 2rem; font-weight: bold; text-align: center; margin: 20px 0; }
            .hire { color: #10b981; } .maybe { color: #f59e0b; } .no-hire { color: #ef4444; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Fast FitScore</h1>
                <p>Ultra-fast candidate evaluation - Text-based testing</p>
            </div>
            
            <form id="evaluationForm">
                <div class="form-group">
                    <label>Resume/Candidate Text</label>
                    <textarea id="resumeText" placeholder="Paste resume content or candidate information here..." required></textarea>
                </div>
                
                <button type="submit" class="analyze-btn">Analyze Candidate</button>
            </form>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            document.getElementById('evaluationForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const text = document.getElementById('resumeText').value;
                if (!text.trim()) {
                    alert('Please enter candidate text');
                    return;
                }
                
                const formData = new FormData();
                formData.append('candidate_text', text);
                
                try {
                    const response = await fetch('/analyze-text', {
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
                        '<div style="color: #ef4444; text-align: center;"><h3>❌ Error</h3><p>' + error.message + '</p></div>';
                    document.getElementById('result').style.display = 'block';
                }
            });
            
            function displayResult(result) {
                let decisionClass = result.hire_decision === 'HIRE' ? 'hire' : 
                                   result.hire_decision.includes('MAYBE') ? 'maybe' : 'no-hire';
                
                const html = `
                    <div class="score ${decisionClass}">${result.overall}/10</div>
                    <div style="text-align: center; margin: 20px 0;">
                        <strong>Decision: ${result.hire_decision}</strong>
                    </div>
                    <div>
                        <p><strong>Education:</strong> ${result.education}/10</p>
                        <p><strong>Experience:</strong> ${result.experience}/10</p>
                        <p><strong>Skills:</strong> ${result.skills}/10</p>
                        <p><strong>Processing Time:</strong> ${result.processing_time}s</p>
                    </div>
                `;
                
                document.getElementById('result').innerHTML = html;
                document.getElementById('result').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """

@app.post("/analyze-text")
def analyze_text(candidate_text: str = Form(...)):
    """Simple text analysis without PDF processing"""
    try:
        if not candidate_text or len(candidate_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Please provide candidate text")
        
        result = evaluate_text(candidate_text)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fast-fitscore-minimal", "version": "1.0.0"} 