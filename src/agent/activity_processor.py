import re
from typing import List, Dict, Any
from collections import Counter
import time

class ActivityStreamProcessor:
    """
    Processes a stream of raw agent activity logs, generating human-readable descriptions,
    detecting patterns, and creating summaries.
    """

    def __init__(self):
        self.pattern_rules = [
            (r"(login|authenticate) successful", "User logged in successfully."),
            (r"(logout|sign out) successful", "User logged out successfully."),
            (r"(failed|error) in.*", "An error occurred."),
            (r"appointment.*(created|scheduled)", "A new appointment was scheduled."),
            (r"appointment.*(cancelled|deleted)", "An appointment was cancelled."),
            (r"patient.*(created|added)", "A new patient record was created."),
        ]

    def process_log(self, log_entry: Dict[str, Any]) -> str:
        """Processes a single log entry and returns a human-readable description."""
        message = log_entry.get("message", "")
        for pattern, description in self.pattern_rules:
            if re.search(pattern, message, re.IGNORECASE):
                return description
        return f"New activity: {message}"

    def process_stream(self, logs: List[Dict[str, Any]]) -> List[str]:
        """Processes a list of log entries."""
        return [self.process_log(log) for log in logs]

    def detect_patterns(self, logs: List[Dict[str, Any]]) -> List[str]:
        """Detects notable patterns in a stream of logs."""
        patterns = []
        log_messages = [log.get("message", "").lower() for log in logs]
        message_counts = Counter(log_messages)

        # High frequency of the same message
        for message, count in message_counts.items():
            if count > 10:
                patterns.append(f"High frequency of message: '{message}' ({count} times).")

        # Multiple failed logins
        failed_logins = sum(1 for msg in log_messages if "login failed" in msg)
        if failed_logins > 3:
            patterns.append(f"Multiple failed login attempts detected ({failed_logins}). Possible security concern.")

        # Rapid succession of events
        timestamps = [log.get("timestamp") for log in logs if log.get("timestamp")]
        if len(timestamps) > 20: # Check for rapid events in larger streams
            time_diffs = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            rapid_events = sum(1 for diff in time_diffs if diff.total_seconds() < 1)
            if rapid_events > 5:
                patterns.append(f"Rapid succession of events detected ({rapid_events} events in under 1 second).")

        return patterns

    def create_summary(self, logs: List[Dict[str, Any]]) -> str:
        """Creates a summary of the activity stream."""
        if not logs:
            return "No activity recorded."
        
        num_logs = len(logs)
        start_time = logs[0].get("timestamp", "N/A")
        end_time = logs[-1].get("timestamp", "N/A")
        
        log_types = [self.process_log(log) for log in logs]
        type_counts = Counter(log_types)
        
        summary = f"Summary: {num_logs} activities recorded from {start_time} to {end_time}.\n"
        summary += "Activity Breakdown:\n"
        for log_type, count in type_counts.most_common(5):
            summary += f"- {log_type}: {count}\n"
            
        return summary

    def performance_benchmark(self, num_logs: int = 10000) -> Dict[str, Any]:
        """Benchmarks the performance of the processor."""
        logs = [{"message": f"test log {i}", "timestamp": time.time()} for i in range(num_logs)]
        
        start_time = time.time()
        self.process_stream(logs)
        end_time = time.time()
        
        processing_time = end_time - start_time
        logs_per_second = num_logs / processing_time
        
        return {
            "num_logs": num_logs,
            "processing_time": processing_time,
            "logs_per_second": logs_per_second
        }

