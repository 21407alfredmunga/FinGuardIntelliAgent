#!/usr/bin/env python3
"""
Quick validation test for Milestone 7 evaluation pipeline.
Tests 2-3 cases to verify the pipeline works end-to-end.
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath('.'))

# Load environment
load_dotenv()

# Import components
from agent.orchestrator import FinGuardIntelliAgent
from agent.evaluator import AgentEvaluator

print("="*80)
print("MILESTONE 7 - EVALUATION PIPELINE VALIDATION TEST")
print("="*80)

# Load golden dataset
print("\n📊 Loading golden dataset...")
with open('data/evaluation/golden_dataset.json', 'r') as f:
    golden_dataset = json.load(f)
print(f"✅ Loaded {len(golden_dataset)} test cases")

# Initialize agent and evaluator
print("\n🤖 Initializing agent and evaluator...")
api_key = os.getenv('GEMINI_API_KEY')
agent = FinGuardIntelliAgent(api_key=api_key)
evaluator = AgentEvaluator(api_key=api_key)
print("✅ Initialization complete")

# Run on first 2 test cases (to avoid rate limits)
test_subset = golden_dataset[:2]
agent_results = []

print(f"\n🔄 Running agent on {len(test_subset)} test cases...")
print("="*80)

for i, test_case in enumerate(test_subset, 1):
    test_id = test_case['test_id']
    query = test_case['query']
    
    print(f"\n[{i}/{len(test_subset)}] Test: {test_id}")
    print(f"Query: {query}")
    print(f"Expected Tool: {test_case['expected_tool']}")
    
    try:
        start_time = time.time()
        
        # Run agent
        result = agent.run(
            user_query=query,
            user_id="validation_test"
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # Extract tools from trace
        trace_logger = result.get('trace_logger')
        trace_logs = trace_logger.logs if trace_logger else []
        
        tools_called = [
            log.get('tool_name') 
            for log in trace_logs 
            if log.get('step_type') == 'ACT' and log.get('tool_name')
        ]
        
        agent_results.append({
            'response': result.get('response', 'No response'),
            'tools_called': tools_called,
            'trace_logs': trace_logs,
            'execution_time_ms': execution_time
        })
        
        print(f"✅ Tools Called: {', '.join(tools_called) if tools_called else 'None'}")
        print(f"⏱️  Execution Time: {execution_time:.0f}ms")
        
        # Wait to avoid rate limits
        if i < len(test_subset):
            print("⏳ Waiting 15s to avoid rate limits...")
            time.sleep(15)
    
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        agent_results.append({
            'response': f"Error: {str(e)}",
            'tools_called': [],
            'trace_logs': [],
            'execution_time_ms': 0
        })
        
        # Wait after errors
        if "429" in str(e) or "quota" in str(e).lower():
            print("⚠️ Rate limit hit. Waiting 60s...")
            time.sleep(60)

print("\n" + "="*80)
print(f"✅ Agent execution complete: {len(agent_results)} results")

# Evaluate with LLM Judge
print("\n⚖️ Starting LLM-as-a-Judge evaluation...")
print("="*80)

evaluations = evaluator.batch_evaluate(
    test_cases=test_subset,
    agent_results=agent_results
)

print(f"\n✅ Evaluation complete: {len(evaluations)} cases graded")

# Display results
print("\n📊 EVALUATION RESULTS")
print("="*80)

for eval_result in evaluations:
    print(f"\nTest ID: {eval_result.test_id}")
    print(f"Query: {eval_result.query}")
    print(f"Expected Tool: {eval_result.expected_tool}")
    print(f"Tools Called: {', '.join(eval_result.tools_called) or 'None'}")
    print(f"Score: {eval_result.judge_evaluation.score:.2f}")
    print(f"Tool Correct: {'✅' if eval_result.judge_evaluation.tool_usage_correct else '❌'}")
    print(f"Goal Achieved: {'✅' if eval_result.judge_evaluation.goal_achieved else '❌'}")
    print(f"Reasoning: {eval_result.judge_evaluation.reasoning[:150]}...")
    print("-"*80)

# Calculate metrics
metrics = AgentEvaluator.calculate_metrics(evaluations)

print("\n📊 AGGREGATE METRICS")
print("="*80)
print(f"Tool Selection Accuracy: {metrics['tool_selection_accuracy']:.1%}")
print(f"Goal Completion Rate: {metrics['goal_completion_rate']:.1%}")
print(f"Pass Rate (Score >= 0.7): {metrics['pass_rate']:.1%}")
print(f"Average Score: {metrics['average_score']:.2f}/1.00")

# Save results
print("\n💾 Saving results to CSV...")
AgentEvaluator.save_results(evaluations, 'data/evaluation/validation_results.csv')
print("✅ Results saved to: data/evaluation/validation_results.csv")

print("\n" + "="*80)
print("✅ VALIDATION TEST COMPLETE!")
print("="*80)
print("\nNext Steps:")
print("1. Run the full evaluation notebook (notebooks/milestone_7_evaluation.ipynb)")
print("2. Review results.csv for detailed analysis")
print("3. Adjust golden dataset based on findings")
