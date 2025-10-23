"""
Logging system for audit trail.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from models.schemas import RequestLog, LogEvent


class Logger:
    """Handles audit logging for the system."""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize Logger.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_log: Optional[RequestLog] = None
    
    def start_request_log(self, request_payload: Dict) -> str:
        """
        Start a new request log.
        
        Args:
            request_payload: The request data
            
        Returns:
            request_id: Unique identifier for this request
        """
        request_id = str(uuid.uuid4())
        
        self.current_log = RequestLog(
            request_id=request_id,
            timestamp=datetime.now(),
            request_payload=request_payload,
            events=[]
        )
        
        return request_id
    
    def log_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        agent_id: Optional[str] = None,
        attempt: Optional[int] = None
    ):
        """
        Log an event in the current request.
        
        Args:
            event_type: Type of event
            data: Event data
            agent_id: Agent identifier (optional)
            attempt: Attempt number (optional)
        """
        if not self.current_log:
            raise RuntimeError("No active request log. Call start_request_log first.")
        
        event = LogEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            agent_id=agent_id,
            attempt=attempt,
            data=data
        )
        
        self.current_log.events.append(event)
    
    def finalize_log(self, response: Optional[Dict] = None, duration: Optional[float] = None):
        """
        Finalize and save the current log.
        
        Args:
            response: Final response data
            duration: Request duration in seconds
        """
        if not self.current_log:
            raise RuntimeError("No active request log.")
        
        self.current_log.response = response
        self.current_log.duration_seconds = duration
        
        # Save to file
        log_filename = f"request_{self.current_log.request_id}_{self.current_log.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        log_path = self.log_dir / log_filename
        
        # Convert to dict and save
        log_dict = self.current_log.model_dump(mode='json')
        
        # Convert datetime objects to strings
        log_dict['timestamp'] = log_dict['timestamp'].isoformat() if isinstance(log_dict['timestamp'], datetime) else log_dict['timestamp']
        for event in log_dict['events']:
            if isinstance(event['timestamp'], datetime):
                event['timestamp'] = event['timestamp'].isoformat()
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_dict, f, indent=2, ensure_ascii=False)
        
        # Clear current log
        self.current_log = None
        
        return log_path
    
    def get_current_log(self) -> Optional[RequestLog]:
        """Get the current active log."""
        return self.current_log
