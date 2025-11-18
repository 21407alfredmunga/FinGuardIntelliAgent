"""
FinGuard IntelliAgent - Agent Logger (Observability)
====================================================

This module implements structured logging for agent execution traces,
capturing the "Think, Act, Observe" trajectory for debugging and monitoring.

Key Concepts Implemented:
- **Observability**: Structured logging of agent reasoning and actions
  [Ref: Prototype to Production p.30]
- **Trace Management**: Unique trace IDs for each agent session
- **Step Tracking**: Logs for Think, Act, and Observe phases

Author: Alfred Munga
License: MIT
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class AgentLogger:
    """
    Structured logger for agent execution traces.
    
    This class captures the complete "Think, Act, Observe" trajectory
    of agent execution, enabling debugging and performance analysis.
    
    Attributes:
        trace_id: Unique identifier for this execution trace
        logs: List of structured log entries
        log_file: Path to JSON log file
    """
    
    def __init__(self, trace_id: Optional[str] = None, log_dir: Optional[str] = None):
        """
        Initialize the agent logger.
        
        Args:
            trace_id: Unique trace ID (generates new if not provided)
            log_dir: Directory for log files (uses default if not provided)
        """
        self.trace_id = trace_id or self._generate_trace_id()
        self.logs: List[Dict[str, Any]] = []
        
        # Setup log directory
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Log file path
        timestamp = datetime.now().strftime("%Y%m%d")
        self.log_file = self.log_dir / f"agent_trace_{timestamp}.jsonl"
        
        logger.info(f"AgentLogger initialized with trace_id={self.trace_id}")
    
    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID."""
        return f"trace_{uuid.uuid4().hex[:12]}"
    
    def log_step(
        self,
        step: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a single step in the agent execution.
        
        Args:
            step: Step type ('think', 'act', 'observe', 'context', 'final')
            content: Step content (reasoning, tool call, observation, etc.)
            metadata: Additional metadata for this step
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'trace_id': self.trace_id,
            'step': step,
            'content': content,
            'metadata': metadata or {}
        }
        
        self.logs.append(log_entry)
        
        # Write to file immediately (append mode)
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log entry: {str(e)}")
    
    def log_think(self, reasoning: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log the 'Think' phase (model reasoning).
        
        Args:
            reasoning: The model's reasoning or thought process
            metadata: Additional context
        """
        self.log_step('think', reasoning, metadata)
        logger.info(f"[THINK] {reasoning[:100]}...")
    
    def log_act(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log the 'Act' phase (tool execution).
        
        Args:
            tool_name: Name of the tool being called
            tool_input: Input parameters for the tool
            metadata: Additional context
        """
        content = {
            'tool_name': tool_name,
            'tool_input': tool_input
        }
        self.log_step('act', content, metadata)
        logger.info(f"[ACT] Calling tool: {tool_name}")
    
    def log_observe(
        self,
        tool_name: str,
        tool_output: Any,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log the 'Observe' phase (tool output).
        
        Args:
            tool_name: Name of the tool that was executed
            tool_output: Output from the tool
            success: Whether the tool execution succeeded
            metadata: Additional context
        """
        content = {
            'tool_name': tool_name,
            'tool_output': tool_output,
            'success': success
        }
        self.log_step('observe', content, metadata)
        
        status = "✅" if success else "❌"
        logger.info(f"[OBSERVE] {status} Tool output received from {tool_name}")
    
    def log_context(self, context_info: Dict[str, Any]) -> None:
        """
        Log context retrieval/preparation.
        
        Args:
            context_info: Information about retrieved context
        """
        self.log_step('context', context_info)
        logger.info(f"[CONTEXT] Loaded context: {list(context_info.keys())}")
    
    def log_final(self, final_response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log the final agent response.
        
        Args:
            final_response: The final answer to the user
            metadata: Additional context (e.g., total steps, duration)
        """
        self.log_step('final', final_response, metadata)
        logger.info(f"[FINAL] Response generated ({len(self.logs)} total steps)")
    
    def log_error(self, error_message: str, error_details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error during agent execution.
        
        Args:
            error_message: Error message
            error_details: Additional error details
        """
        content = {
            'error_message': error_message,
            'error_details': error_details or {}
        }
        self.log_step('error', content)
        logger.error(f"[ERROR] {error_message}")
    
    def get_trajectory(self) -> List[Dict[str, Any]]:
        """
        Get the complete execution trajectory.
        
        Returns:
            List of all log entries in chronological order
        """
        return self.logs.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the execution trace.
        
        Returns:
            Summary statistics about the execution
        """
        think_count = sum(1 for log in self.logs if log['step'] == 'think')
        act_count = sum(1 for log in self.logs if log['step'] == 'act')
        observe_count = sum(1 for log in self.logs if log['step'] == 'observe')
        error_count = sum(1 for log in self.logs if log['step'] == 'error')
        
        # Calculate success rate
        successful_observations = sum(
            1 for log in self.logs 
            if log['step'] == 'observe' and log['content'].get('success', False)
        )
        success_rate = (successful_observations / observe_count * 100) if observe_count > 0 else 0
        
        # Get tool usage
        tools_used = [
            log['content']['tool_name']
            for log in self.logs
            if log['step'] == 'act'
        ]
        
        return {
            'trace_id': self.trace_id,
            'total_steps': len(self.logs),
            'think_count': think_count,
            'act_count': act_count,
            'observe_count': observe_count,
            'error_count': error_count,
            'success_rate': success_rate,
            'tools_used': tools_used,
            'duration': self._calculate_duration(),
            'log_file': str(self.log_file)
        }
    
    def _calculate_duration(self) -> Optional[float]:
        """Calculate total execution duration in seconds."""
        if len(self.logs) < 2:
            return None
        
        try:
            start_time = datetime.fromisoformat(self.logs[0]['timestamp'])
            end_time = datetime.fromisoformat(self.logs[-1]['timestamp'])
            duration = (end_time - start_time).total_seconds()
            return round(duration, 2)
        except Exception:
            return None
    
    def print_trajectory(self) -> None:
        """Print a human-readable trajectory of the execution."""
        print("=" * 70)
        print(f"AGENT EXECUTION TRAJECTORY (Trace ID: {self.trace_id})")
        print("=" * 70)
        
        for i, log in enumerate(self.logs, 1):
            step = log['step'].upper()
            timestamp = log['timestamp'].split('T')[1].split('.')[0]
            
            print(f"\n{i}. [{timestamp}] {step}")
            print("-" * 70)
            
            if step == 'THINK':
                print(f"💭 Reasoning: {log['content']}")
            
            elif step == 'ACT':
                tool_name = log['content']['tool_name']
                tool_input = log['content']['tool_input']
                print(f"🔧 Tool: {tool_name}")
                print(f"   Input: {json.dumps(tool_input, indent=2)}")
            
            elif step == 'OBSERVE':
                tool_name = log['content']['tool_name']
                success = log['content']['success']
                status = "✅ Success" if success else "❌ Failed"
                print(f"👁️  {status} from {tool_name}")
                
                # Print abbreviated output
                output = log['content']['tool_output']
                if isinstance(output, dict) and len(str(output)) > 200:
                    print(f"   Output: {str(output)[:200]}...")
                else:
                    print(f"   Output: {output}")
            
            elif step == 'CONTEXT':
                print(f"📚 Context loaded: {list(log['content'].keys())}")
            
            elif step == 'FINAL':
                print(f"✅ Final Response: {log['content']}")
            
            elif step == 'ERROR':
                print(f"❌ Error: {log['content']['error_message']}")
        
        # Print summary
        print("\n" + "=" * 70)
        summary = self.get_summary()
        print(f"SUMMARY:")
        print(f"  Total Steps: {summary['total_steps']}")
        print(f"  Tools Used: {len(summary['tools_used'])} ({', '.join(set(summary['tools_used']))})")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        if summary['duration']:
            print(f"  Duration: {summary['duration']}s")
        print("=" * 70)


# ============================================================================
# Session Store for Multi-Turn Conversations
# ============================================================================

class SessionStore:
    """
    Manages conversation sessions with history tracking.
    
    This class maintains conversation history across multiple turns,
    enabling context-aware responses and memory persistence.
    
    Attributes:
        sessions: Dictionary mapping user_id to conversation history
        max_history: Maximum number of turns to keep in memory
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize the session store.
        
        Args:
            max_history: Maximum number of conversation turns to keep
        """
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.max_history = max_history
        logger.info(f"SessionStore initialized (max_history={max_history})")
    
    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of conversation turns (role + content)
        """
        return self.sessions.get(user_id, [])
    
    def add_turn(self, user_id: str, role: str, content: str) -> None:
        """
        Add a conversation turn to the session.
        
        Args:
            user_id: User identifier
            role: Role ('user', 'assistant', 'system')
            content: Message content
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = []
        
        self.sessions[user_id].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Trim history if needed (keep most recent)
        if len(self.sessions[user_id]) > self.max_history:
            self.sessions[user_id] = self.sessions[user_id][-self.max_history:]
        
        logger.info(f"Added turn for user {user_id} (role={role})")
    
    def clear_session(self, user_id: str) -> None:
        """Clear conversation history for a user."""
        if user_id in self.sessions:
            del self.sessions[user_id]
            logger.info(f"Cleared session for user {user_id}")


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """Test the logger functionality."""
    
    print("=" * 70)
    print("AgentLogger Test")
    print("=" * 70)
    
    # Create logger
    trace_logger = AgentLogger()
    
    # Simulate agent execution
    trace_logger.log_context({
        'user_profile': {'name': 'Jane', 'business': 'Retail'},
        'memories_retrieved': 2
    })
    
    trace_logger.log_think("User wants to know about unpaid invoices. I should use GetUnpaidInvoicesTool.")
    
    trace_logger.log_act(
        tool_name='GetUnpaidInvoicesTool',
        tool_input={'user_id': 'jane_doe'}
    )
    
    trace_logger.log_observe(
        tool_name='GetUnpaidInvoicesTool',
        tool_output={'total_count': 3, 'total_amount': 125000},
        success=True
    )
    
    trace_logger.log_think("I have the unpaid invoices. Now I'll format a response for the user.")
    
    trace_logger.log_final("You have 3 unpaid invoices totaling KES 125,000.")
    
    # Print trajectory
    trace_logger.print_trajectory()
    
    # Print summary
    print("\n📊 Execution Summary:")
    summary = trace_logger.get_summary()
    print(json.dumps(summary, indent=2))
    
    print(f"\n✅ Logs saved to: {trace_logger.log_file}")
