#!/usr/bin/env python3
"""
Test script for the optimized FitScore implementation
"""

import sys
import os
import asyncio
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

try:
    from agents.fitscore.src.optimized_fitscore import OptimizedFitScore, EliteScore
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"❌ Import failed: {e}")
    IMPORT_SUCCESS = False

async def test_optimized_fitscore():
    """Test the optimized FitScore system"""
    if not IMPORT_SUCCESS:
        return
    
    print("🚀 Testing Optimized FitScore System")
    print("=" * 50)
    
    # Initialize the system
    fitscore_engine = OptimizedFitScore()
    
    # Test cases
    test_cases = [
        {
            "name": "Elite Software Engineer",
            "text": """
            John Smith
            Senior Software Engineer
            
            Education:
            Stanford University, B.S. Computer Science, 2018
            
            Experience:
            Google (2018-2021): Software Engineer
            - Built scalable microservices handling 50M+ requests/day
            - Led team of 5 engineers on critical infrastructure projects
            - Optimized system performance by 60%
            
            Meta (2021-2023): Senior Software Engineer  
            - Technical lead for cross-platform development
            - Mentored 8 junior engineers
            - Shipped features used by 500M+ users
            
            Stripe (2023-Present): Staff Engineer
            - Principal architect for payment processing systems
            - Led company-wide platform migration
            - Founded internal developer tools team
            
            Skills: Python, JavaScript, React, Node.js, Kubernetes, AWS, System Design
            Achievements: Published 3 papers, Open source contributor, Patent holder
            """,
            "role": "software_engineer"
        },
        {
            "name": "Good Product Manager",
            "text": """
            Sarah Johnson
            Product Manager
            
            Education:
            UC Berkeley, B.A. Economics, 2019
            
            Experience:
            McKinsey & Company (2019-2021): Business Analyst
            - Led strategic initiatives for Fortune 500 clients
            - Analyzed market opportunities worth $100M+
            
            Airbnb (2021-2023): Associate Product Manager
            - Launched 3 major features impacting 10M+ users
            - Increased user engagement by 25%
            - Led cross-functional team of 12 people
            
            Skills: Product Strategy, Analytics, A/B Testing, SQL, User Research
            Achievements: Shipped 0-1 product, Revenue growth initiatives
            """,
            "role": "product_manager"
        },
        {
            "name": "Junior Data Scientist",
            "text": """
            Mike Chen
            Data Scientist
            
            Education:
            University of Michigan, B.S. Statistics, 2022
            
            Experience:
            Tesla (2022-Present): Junior Data Scientist
            - Built ML models for predictive maintenance
            - Analyzed vehicle performance data
            - Created dashboards for engineering teams
            
            Skills: Python, R, SQL, Machine Learning, Pandas, scikit-learn
            """,
            "role": "data_scientist"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['name']}")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            result = await fitscore_engine.evaluate_candidate_fast(
                candidate_text=test_case["text"],
                role=test_case["role"]
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"Overall Score: {result.overall}/10")
            print(f"Education: {result.education}/10")
            print(f"Experience: {result.experience}/10") 
            print(f"Skills: {result.skills}/10")
            print(f"Achievements: {result.achievements}/10")
            print(f"Hire Decision: {result.hire_decision}")
            print(f"Confidence: {result.confidence}%")
            print(f"Processing Time: {processing_time:.3f}s")
            
            if result.strengths:
                print(f"Strengths: {', '.join(result.strengths)}")
            if result.concerns:
                print(f"Concerns: {', '.join(result.concerns)}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Optimized FitScore Testing Complete!")

async def test_batch_processing():
    """Test batch processing capability"""
    if not IMPORT_SUCCESS:
        return
        
    print("\n🚀 Testing Batch Processing")
    print("=" * 50)
    
    fitscore_engine = OptimizedFitScore()
    
    # Create batch of candidates
    candidates = [
        ("Stanford CS grad, Google SWE, 5 years experience", "candidate_1"),
        ("MIT grad, Facebook PM, shipped major features", "candidate_2"), 
        ("Berkeley data scientist, Tesla ML engineer", "candidate_3"),
    ]
    
    start_time = time.time()
    results = await fitscore_engine.batch_evaluate(candidates, "software_engineer")
    batch_time = time.time() - start_time
    
    print(f"Processed {len(candidates)} candidates in {batch_time:.2f}s")
    print(f"Average time per candidate: {batch_time/len(candidates):.2f}s")
    
    for i, result in enumerate(results):
        print(f"Candidate {i+1}: {result.overall}/10 ({result.hire_decision})")

def main():
    """Main test function"""
    print("🧪 FitScore Optimization Test Suite")
    print("=" * 50)
    
    if IMPORT_SUCCESS:
        print("✅ Imports successful")
    else:
        print("❌ Import failed - using mock implementation")
        return
    
    # Run tests
    asyncio.run(test_optimized_fitscore())
    asyncio.run(test_batch_processing())

if __name__ == "__main__":
    main() 