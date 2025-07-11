import threading
import time
import datetime
from typing import Dict, List, Any, Optional
from collections import deque
import json
import os
from pathlib import Path

class StreamingHandler:
    """Handles real-time updates and progress tracking for TradingAgents analysis."""
    
    def __init__(self, max_messages: int = 1000):
        self.max_messages = max_messages
        self.reset()
        
    def reset(self):
        """Reset the handler state."""
        self.messages = deque(maxlen=self.max_messages)
        self.agent_status = {
            # Analyst Team
            "Market Analyst": "pending",
            "Social Analyst": "pending", 
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            # Research Team
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            # Trading Team
            "Trader": "pending",
            # Risk Management Team
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            # Portfolio Management Team
            "Portfolio Manager": "pending",
        }
        self.reports = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }
        self.current_ticker = None
        self.current_date = None
        self.analysis_start_time = None
        self.analysis_end_time = None
        self.error_messages = []
        self._lock = threading.Lock()
        
    def set_analysis_params(self, ticker: str, date: str):
        """Set analysis parameters."""
        with self._lock:
            self.current_ticker = ticker
            self.current_date = date
            self.analysis_start_time = datetime.datetime.now()
            self.add_message("info", f"Starting analysis for {ticker} on {date}")
    
    def add_message(self, message_type: str, content: str, agent: Optional[str] = None):
        """Add a message to the stream."""
        with self._lock:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            message = {
                "timestamp": timestamp,
                "type": message_type,
                "content": content,
                "agent": agent,
                "message": content
            }
            self.messages.append(message)
            
            # If this is an agent-specific message, update agent status
            if agent and message_type in ["start", "running", "completed", "error"]:
                self.update_agent_status(agent, message_type)
    
    def update_agent_status(self, agent: str, status: str):
        """Update status of a specific agent."""
        with self._lock:
            if agent in self.agent_status:
                # Map message types to status
                status_mapping = {
                    "start": "running",
                    "running": "running", 
                    "completed": "completed",
                    "error": "error",
                    "pending": "pending"
                }
                
                new_status = status_mapping.get(status, status)
                self.agent_status[agent] = new_status
                
                # Add status update message
                self.add_message(
                    "status", 
                    f"{agent} status: {new_status}",
                    agent
                )
    
    def update_report(self, report_type: str, content: str):
        """Update a specific report."""
        with self._lock:
            if report_type in self.reports:
                self.reports[report_type] = content
                self.add_message("report", f"Updated {report_type.replace('_', ' ').title()}")
    
    def get_latest_updates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the latest updates."""
        with self._lock:
            return list(self.messages)[-limit:]
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Get all messages."""
        with self._lock:
            return list(self.messages)
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get current agent status."""
        with self._lock:
            return self.agent_status.copy()
    
    def get_report(self, report_type: str) -> Optional[str]:
        """Get a specific report."""
        with self._lock:
            return self.reports.get(report_type)
    
    def get_all_reports(self) -> Dict[str, Optional[str]]:
        """Get all reports."""
        with self._lock:
            return self.reports.copy()
    
    def add_error(self, error: str, agent: Optional[str] = None):
        """Add an error message."""
        with self._lock:
            self.error_messages.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "error": error,
                "agent": agent
            })
            self.add_message("error", f"Error: {error}", agent)
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all error messages."""
        with self._lock:
            return self.error_messages.copy()
    
    def mark_analysis_complete(self, success: bool = True):
        """Mark analysis as complete."""
        with self._lock:
            self.analysis_end_time = datetime.datetime.now()
            if success:
                self.add_message("success", "Analysis completed successfully")
            else:
                self.add_message("error", "Analysis failed")
    
    def get_analysis_duration(self) -> Optional[float]:
        """Get analysis duration in seconds."""
        with self._lock:
            if self.analysis_start_time and self.analysis_end_time:
                return (self.analysis_end_time - self.analysis_start_time).total_seconds()
            elif self.analysis_start_time:
                return (datetime.datetime.now() - self.analysis_start_time).total_seconds()
            return None
    
    def get_completion_percentage(self) -> float:
        """Get estimated completion percentage based on agent status."""
        with self._lock:
            total_agents = len(self.agent_status)
            completed_agents = sum(1 for status in self.agent_status.values() if status == "completed")
            return (completed_agents / total_agents) * 100 if total_agents > 0 else 0
    
    def get_active_agents(self) -> List[str]:
        """Get list of currently active (running) agents."""
        with self._lock:
            return [agent for agent, status in self.agent_status.items() if status == "running"]
    
    def get_completed_agents(self) -> List[str]:
        """Get list of completed agents."""
        with self._lock:
            return [agent for agent, status in self.agent_status.items() if status == "completed"]
    
    def get_pending_agents(self) -> List[str]:
        """Get list of pending agents."""
        with self._lock:
            return [agent for agent, status in self.agent_status.items() if status == "pending"]
    
    def get_failed_agents(self) -> List[str]:
        """Get list of failed agents."""
        with self._lock:
            return [agent for agent, status in self.agent_status.items() if status == "error"]
    
    def export_to_json(self, include_messages: bool = True) -> str:
        """Export handler state to JSON."""
        with self._lock:
            export_data = {
                "ticker": self.current_ticker,
                "date": self.current_date,
                "analysis_start_time": self.analysis_start_time.isoformat() if self.analysis_start_time else None,
                "analysis_end_time": self.analysis_end_time.isoformat() if self.analysis_end_time else None,
                "duration_seconds": self.get_analysis_duration(),
                "completion_percentage": self.get_completion_percentage(),
                "agent_status": self.agent_status,
                "reports": self.reports,
                "errors": self.error_messages,
                "summary": {
                    "total_agents": len(self.agent_status),
                    "completed_agents": len(self.get_completed_agents()),
                    "active_agents": len(self.get_active_agents()),
                    "pending_agents": len(self.get_pending_agents()),
                    "failed_agents": len(self.get_failed_agents()),
                }
            }
            
            if include_messages:
                export_data["messages"] = list(self.messages)
            
            return json.dumps(export_data, indent=2)
    
    def save_to_file(self, file_path: str):
        """Save handler state to file."""
        try:
            with open(file_path, 'w') as f:
                f.write(self.export_to_json())
            self.add_message("info", f"Saved analysis state to {file_path}")
        except Exception as e:
            self.add_error(f"Failed to save to file: {str(e)}")
    
    def load_from_file(self, file_path: str):
        """Load handler state from file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            with self._lock:
                self.current_ticker = data.get("ticker")
                self.current_date = data.get("date")
                
                if data.get("analysis_start_time"):
                    self.analysis_start_time = datetime.datetime.fromisoformat(data["analysis_start_time"])
                
                if data.get("analysis_end_time"):
                    self.analysis_end_time = datetime.datetime.fromisoformat(data["analysis_end_time"])
                
                self.agent_status.update(data.get("agent_status", {}))
                self.reports.update(data.get("reports", {}))
                self.error_messages = data.get("errors", [])
                
                if "messages" in data:
                    self.messages = deque(data["messages"], maxlen=self.max_messages)
            
            self.add_message("info", f"Loaded analysis state from {file_path}")
            
        except Exception as e:
            self.add_error(f"Failed to load from file: {str(e)}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        with self._lock:
            return {
                "ticker": self.current_ticker,
                "date": self.current_date,
                "duration_seconds": self.get_analysis_duration(),
                "completion_percentage": self.get_completion_percentage(),
                "total_agents": len(self.agent_status),
                "completed_agents": len(self.get_completed_agents()),
                "active_agents": len(self.get_active_agents()),
                "pending_agents": len(self.get_pending_agents()),
                "failed_agents": len(self.get_failed_agents()),
                "total_messages": len(self.messages),
                "total_errors": len(self.error_messages),
                "reports_generated": len([r for r in self.reports.values() if r is not None])
            }
    
    def format_status_display(self) -> str:
        """Format status for display."""
        summary = self.get_summary()
        
        status_lines = []
        status_lines.append(f"**Analysis Status for {summary['ticker']} on {summary['date']}**")
        status_lines.append("")
        
        if summary['duration_seconds']:
            duration = int(summary['duration_seconds'])
            minutes = duration // 60
            seconds = duration % 60
            status_lines.append(f"**Duration:** {minutes}m {seconds}s")
        
        status_lines.append(f"**Progress:** {summary['completion_percentage']:.1f}%")
        status_lines.append(f"**Completed:** {summary['completed_agents']}/{summary['total_agents']} agents")
        
        if summary['active_agents'] > 0:
            active_agents = self.get_active_agents()
            status_lines.append(f"**Active:** {', '.join(active_agents)}")
        
        if summary['failed_agents'] > 0:
            failed_agents = self.get_failed_agents()
            status_lines.append(f"**Failed:** {', '.join(failed_agents)}")
        
        status_lines.append(f"**Reports Generated:** {summary['reports_generated']}/7")
        
        return "\n".join(status_lines)