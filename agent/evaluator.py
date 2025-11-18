"""
agent/evaluator.py

LLM-as-a-Judge Evaluator for FinGuard IntelliAgent.

This module implements automated quality assessment using the "LLM-as-a-Judge" pattern,
where a model grades the agent's responses based on specific criteria.

References:
- Intro to Agents p.29: "Since outputs are probabilistic, use a model to grade responses"
- Prototype to Production p.12: "Assess not just the final answer, but the Trajectory"

Author: Alfred Munga
Date: November 18, 2025
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===========================
# Pydantic Models for Structured Output
# ===========================

class JudgeEvaluation(BaseModel):
    """
    Structured output from the LLM Judge.
    
    Enforces strict schema for evaluation results to ensure consistency
    across multiple test cases.
    """
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall score (0.0 = complete failure, 1.0 = perfect execution)"
    )
    tool_usage_correct: bool = Field(
        ...,
        description="Whether the agent called the correct tool(s)"
    )
    goal_achieved: bool = Field(
        ...,
        description="Whether the agent achieved the intended goal"
    )
    idempotency_respected: bool = Field(
        default=True,
        description="Whether idempotency checks were performed when required"
    )
    reasoning: str = Field(
        ...,
        min_length=10,
        description="Detailed explanation of the evaluation"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of specific issues or failures found"
    )
    
    @field_validator('reasoning')
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        """Ensure reasoning is not just a placeholder."""
        if v.strip().lower() in ['n/a', 'none', '']:
            raise ValueError("Reasoning must be a substantive explanation")
        return v


class EvaluationResult(BaseModel):
    """
    Complete evaluation result for a single test case.
    
    Combines test case metadata with judge evaluation and execution traces.
    """
    test_id: str
    query: str
    expected_tool: str
    expected_intent: str
    category: str
    difficulty: str
    
    # Execution results
    agent_response: str
    tools_called: List[str] = Field(default_factory=list)
    execution_time_ms: float
    
    # Judge evaluation
    judge_evaluation: JudgeEvaluation
    
    # Metadata
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    model_used: str = "gemini-2.5-flash"


# ===========================
# Agent Evaluator Class
# ===========================

class AgentEvaluator:
    """
    LLM-as-a-Judge evaluator for agent responses.
    
    Uses Gemini to grade agent outputs based on:
    1. Tool Selection (Trajectory evaluation)
    2. Goal Completion (Task success)
    3. Idempotency (Safety checks)
    4. Response Quality (Correctness and tone)
    
    Reference: Intro to Agents p.29 - "Use a model to grade responses based on criteria"
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the evaluator with Gemini model.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model_name: Model to use for judging (default: gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or arguments")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"AgentEvaluator initialized with model: {model_name}")
    
    def _build_judge_prompt(
        self,
        query: str,
        expected_tool: str,
        expected_intent: str,
        criteria: str,
        agent_response: str,
        tools_called: List[str],
        trace_logs: List[Dict[str, Any]]
    ) -> str:
        """
        Construct the judge prompt for evaluation.
        
        The prompt instructs the judge to assess:
        - Tool selection accuracy (Trajectory)
        - Goal completion
        - Idempotency checks
        - Response correctness
        
        Args:
            query: User's original query
            expected_tool: Tool that should have been called
            expected_intent: Expected agent intent
            criteria: Specific success criteria
            agent_response: Agent's final response
            tools_called: List of tools the agent actually called
            trace_logs: Execution trace logs
        
        Returns:
            Formatted judge prompt string
        """
        # Extract key information from trace logs
        think_steps = [log for log in trace_logs if log.get('step_type') == 'THINK']
        act_steps = [log for log in trace_logs if log.get('step_type') == 'ACT']
        observe_steps = [log for log in trace_logs if log.get('step_type') == 'OBSERVE']
        
        prompt = f"""You are an expert AI QA auditor evaluating an AI agent's performance.

**EVALUATION TASK:**
Compare the agent's actual execution against the expected behavior and grade it objectively.

**USER QUERY:**
"{query}"

**EXPECTED BEHAVIOR:**
- Intent: {expected_intent}
- Tool to Use: {expected_tool}
- Success Criteria: {criteria}

**AGENT'S ACTUAL EXECUTION:**

Tools Called: {', '.join(tools_called) if tools_called else 'None'}

Agent's Final Response:
{agent_response}

**EXECUTION TRACE:**
- Think Steps: {len(think_steps)}
- Act Steps (Tool Calls): {len(act_steps)}
- Observe Steps: {len(observe_steps)}

Detailed Tool Calls:
"""
        
        for i, act in enumerate(act_steps, 1):
            tool_name = act.get('tool_name', 'Unknown')
            tool_input = act.get('tool_input', {})
            prompt += f"\n{i}. Tool: {tool_name}\n   Input: {json.dumps(tool_input, indent=2)}\n"
        
        prompt += f"""

**EVALUATION CRITERIA:**

1. **Tool Selection Accuracy (Trajectory):**
   - Did the agent call the expected tool(s)?
   - Were the tools called in the right order for multi-step tasks?

2. **Goal Achievement:**
   - Did the agent successfully complete the user's request?
   - Is the final response accurate and helpful?

3. **Idempotency & Safety:**
   - For action tasks (e.g., send_payment_request), did the agent check status first?
   - Were duplicate actions prevented?

4. **Response Quality:**
   - Is the response clear, professional, and correctly formatted?
   - Does it address the user's query directly?

**YOUR TASK:**
Provide a structured evaluation with:
- **score** (0.0 to 1.0): Overall grade
- **tool_usage_correct** (true/false): Whether correct tool(s) were used
- **goal_achieved** (true/false): Whether the task was completed successfully
- **idempotency_respected** (true/false): Whether safety checks were performed (if applicable)
- **reasoning** (string): Detailed explanation (min 50 words)
- **issues** (array of strings): Specific problems found (or empty if none)

**OUTPUT FORMAT (JSON):**
{{
  "score": 0.85,
  "tool_usage_correct": true,
  "goal_achieved": true,
  "idempotency_respected": true,
  "reasoning": "The agent correctly identified the user's intent and called the get_unpaid_invoices tool...",
  "issues": []
}}

Be objective and thorough. Grade strictly based on the criteria.
"""
        
        return prompt
    
    def evaluate_response(
        self,
        query: str,
        expected_tool: str,
        expected_intent: str,
        criteria: str,
        agent_response: str,
        tools_called: List[str],
        trace_logs: List[Dict[str, Any]],
        category: str = "general"
    ) -> JudgeEvaluation:
        """
        Evaluate an agent's response using LLM-as-a-Judge.
        
        This is the core evaluation method that:
        1. Constructs a judge prompt with all context
        2. Calls Gemini to grade the response
        3. Parses the structured output
        4. Returns a JudgeEvaluation object
        
        Reference: Prototype to Production p.12 - "Assess the Trajectory, not just the answer"
        
        Args:
            query: User's original query
            expected_tool: Tool that should have been called
            expected_intent: Expected agent intent
            criteria: Specific success criteria
            agent_response: Agent's final response
            tools_called: List of tools actually called
            trace_logs: Execution trace logs
            category: Test category (for analytics)
        
        Returns:
            JudgeEvaluation object with structured assessment
        
        Raises:
            ValueError: If judge output cannot be parsed
        """
        logger.info(f"Evaluating response for query: '{query[:50]}...'")
        
        try:
            # Build the judge prompt
            judge_prompt = self._build_judge_prompt(
                query=query,
                expected_tool=expected_tool,
                expected_intent=expected_intent,
                criteria=criteria,
                agent_response=agent_response,
                tools_called=tools_called,
                trace_logs=trace_logs
            )
            
            # Call Gemini to judge
            response = self.model.generate_content(judge_prompt)
            judge_output = response.text.strip()
            
            # Parse JSON output
            # Extract JSON from markdown code blocks if present
            if "```json" in judge_output:
                judge_output = judge_output.split("```json")[1].split("```")[0].strip()
            elif "```" in judge_output:
                judge_output = judge_output.split("```")[1].split("```")[0].strip()
            
            judge_dict = json.loads(judge_output)
            
            # Validate and create JudgeEvaluation
            evaluation = JudgeEvaluation(**judge_dict)
            
            logger.info(f"✅ Evaluation complete - Score: {evaluation.score:.2f}, "
                       f"Tool Correct: {evaluation.tool_usage_correct}, "
                       f"Goal Achieved: {evaluation.goal_achieved}")
            
            return evaluation
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse judge output as JSON: {e}")
            logger.error(f"Raw output: {judge_output}")
            
            # Fallback: Create a failed evaluation
            return JudgeEvaluation(
                score=0.0,
                tool_usage_correct=False,
                goal_achieved=False,
                idempotency_respected=False,
                reasoning=f"Judge output parsing failed: {str(e)}",
                issues=["Judge output was not valid JSON"]
            )
        
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return JudgeEvaluation(
                score=0.0,
                tool_usage_correct=False,
                goal_achieved=False,
                idempotency_respected=False,
                reasoning=f"Evaluation error: {str(e)}",
                issues=[f"Exception during evaluation: {type(e).__name__}"]
            )
    
    def batch_evaluate(
        self,
        test_cases: List[Dict[str, Any]],
        agent_results: List[Dict[str, Any]]
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple test cases in batch.
        
        Args:
            test_cases: List of test case dictionaries from golden dataset
            agent_results: List of agent execution results
        
        Returns:
            List of EvaluationResult objects
        """
        if len(test_cases) != len(agent_results):
            raise ValueError("Number of test cases must match number of agent results")
        
        logger.info(f"Starting batch evaluation of {len(test_cases)} test cases")
        
        evaluations = []
        for test_case, agent_result in zip(test_cases, agent_results):
            try:
                # Evaluate this test case
                judge_eval = self.evaluate_response(
                    query=test_case['query'],
                    expected_tool=test_case['expected_tool'],
                    expected_intent=test_case['expected_intent'],
                    criteria=test_case['criteria'],
                    agent_response=agent_result['response'],
                    tools_called=agent_result['tools_called'],
                    trace_logs=agent_result['trace_logs'],
                    category=test_case['category']
                )
                
                # Create complete evaluation result
                eval_result = EvaluationResult(
                    test_id=test_case['test_id'],
                    query=test_case['query'],
                    expected_tool=test_case['expected_tool'],
                    expected_intent=test_case['expected_intent'],
                    category=test_case['category'],
                    difficulty=test_case['difficulty'],
                    agent_response=agent_result['response'],
                    tools_called=agent_result['tools_called'],
                    execution_time_ms=agent_result['execution_time_ms'],
                    judge_evaluation=judge_eval
                )
                
                evaluations.append(eval_result)
                
            except Exception as e:
                logger.error(f"Failed to evaluate test case {test_case['test_id']}: {e}")
                # Create a failed evaluation result
                evaluations.append(EvaluationResult(
                    test_id=test_case['test_id'],
                    query=test_case['query'],
                    expected_tool=test_case['expected_tool'],
                    expected_intent=test_case['expected_intent'],
                    category=test_case['category'],
                    difficulty=test_case.get('difficulty', 'unknown'),
                    agent_response="Evaluation failed",
                    tools_called=[],
                    execution_time_ms=0,
                    judge_evaluation=JudgeEvaluation(
                        score=0.0,
                        tool_usage_correct=False,
                        goal_achieved=False,
                        reasoning=f"Evaluation error: {str(e)}",
                        issues=[str(e)]
                    )
                ))
        
        logger.info(f"✅ Batch evaluation complete: {len(evaluations)} results")
        return evaluations
    
    @staticmethod
    def calculate_metrics(evaluations: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Calculate aggregate metrics from evaluation results.
        
        Metrics:
        - Tool Selection Accuracy: % of times correct tool was called
        - Goal Completion Rate: % of PASS grades (score >= 0.7)
        - Average Score: Mean score across all tests
        - Idempotency Compliance: % respecting safety checks
        
        Reference: Intro to Agents p.29 - "Track Goal Completion Rate"
        
        Args:
            evaluations: List of EvaluationResult objects
        
        Returns:
            Dictionary with aggregate metrics
        """
        if not evaluations:
            return {
                "total_tests": 0,
                "tool_selection_accuracy": 0.0,
                "goal_completion_rate": 0.0,
                "average_score": 0.0,
                "idempotency_compliance": 0.0
            }
        
        total = len(evaluations)
        tool_correct_count = sum(1 for e in evaluations if e.judge_evaluation.tool_usage_correct)
        goal_achieved_count = sum(1 for e in evaluations if e.judge_evaluation.goal_achieved)
        pass_count = sum(1 for e in evaluations if e.judge_evaluation.score >= 0.7)
        idempotency_count = sum(1 for e in evaluations if e.judge_evaluation.idempotency_respected)
        
        total_score = sum(e.judge_evaluation.score for e in evaluations)
        
        # Breakdown by category
        categories = {}
        for eval_result in evaluations:
            cat = eval_result.category
            if cat not in categories:
                categories[cat] = {"count": 0, "passed": 0, "avg_score": 0.0}
            categories[cat]["count"] += 1
            if eval_result.judge_evaluation.score >= 0.7:
                categories[cat]["passed"] += 1
            categories[cat]["avg_score"] += eval_result.judge_evaluation.score
        
        # Calculate category averages
        for cat, data in categories.items():
            data["avg_score"] = data["avg_score"] / data["count"] if data["count"] > 0 else 0.0
            data["pass_rate"] = data["passed"] / data["count"] if data["count"] > 0 else 0.0
        
        metrics = {
            "total_tests": total,
            "tool_selection_accuracy": tool_correct_count / total,
            "goal_completion_rate": goal_achieved_count / total,
            "pass_rate": pass_count / total,
            "average_score": total_score / total,
            "idempotency_compliance": idempotency_count / total,
            "category_breakdown": categories
        }
        
        logger.info(f"📊 Metrics calculated: "
                   f"Tool Accuracy={metrics['tool_selection_accuracy']:.1%}, "
                   f"Goal Completion={metrics['goal_completion_rate']:.1%}, "
                   f"Pass Rate={metrics['pass_rate']:.1%}")
        
        return metrics
    
    @staticmethod
    def save_results(
        evaluations: List[EvaluationResult],
        output_path: str = "data/evaluation/results.csv"
    ):
        """
        Save evaluation results to CSV for tracking over time.
        
        Args:
            evaluations: List of EvaluationResult objects
            output_path: Path to output CSV file
        """
        import csv
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            fieldnames = [
                'test_id', 'query', 'expected_tool', 'category', 'difficulty',
                'tools_called', 'score', 'tool_usage_correct', 'goal_achieved',
                'idempotency_respected', 'reasoning', 'issues', 'execution_time_ms', 'timestamp'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for eval_result in evaluations:
                writer.writerow({
                    'test_id': eval_result.test_id,
                    'query': eval_result.query,
                    'expected_tool': eval_result.expected_tool,
                    'category': eval_result.category,
                    'difficulty': eval_result.difficulty,
                    'tools_called': ', '.join(eval_result.tools_called),
                    'score': eval_result.judge_evaluation.score,
                    'tool_usage_correct': eval_result.judge_evaluation.tool_usage_correct,
                    'goal_achieved': eval_result.judge_evaluation.goal_achieved,
                    'idempotency_respected': eval_result.judge_evaluation.idempotency_respected,
                    'reasoning': eval_result.judge_evaluation.reasoning,
                    'issues': '; '.join(eval_result.judge_evaluation.issues),
                    'execution_time_ms': eval_result.execution_time_ms,
                    'timestamp': eval_result.timestamp
                })
        
        logger.info(f"✅ Results saved to {output_path}")


# ===========================
# Testing (if run directly)
# ===========================

if __name__ == "__main__":
    import sys
    
    # Simple test to verify the evaluator works
    print("Testing AgentEvaluator with a sample case...\n")
    
    try:
        evaluator = AgentEvaluator()
        
        # Mock test case
        test_query = "Show me my unpaid invoices."
        test_response = "You have 7 unpaid invoices totaling KES 427,574.37."
        test_tools = ["get_unpaid_invoices"]
        test_trace = [
            {"step_type": "THINK", "iteration": 1},
            {"step_type": "ACT", "tool_name": "get_unpaid_invoices", "tool_input": {}},
            {"step_type": "OBSERVE", "success": True}
        ]
        
        evaluation = evaluator.evaluate_response(
            query=test_query,
            expected_tool="get_unpaid_invoices",
            expected_intent="information_retrieval",
            criteria="Must retrieve unpaid invoices with essential fields.",
            agent_response=test_response,
            tools_called=test_tools,
            trace_logs=test_trace
        )
        
        print(f"✅ Score: {evaluation.score:.2f}")
        print(f"✅ Tool Usage Correct: {evaluation.tool_usage_correct}")
        print(f"✅ Goal Achieved: {evaluation.goal_achieved}")
        print(f"\n📝 Reasoning:\n{evaluation.reasoning}")
        
        if evaluation.issues:
            print(f"\n⚠️ Issues Found:")
            for issue in evaluation.issues:
                print(f"  - {issue}")
        
        print("\n✅ AgentEvaluator test passed!")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
