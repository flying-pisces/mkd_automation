"""
Week 4 Test Logger

Simple test logging functionality for Week 4 tests.
"""

import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class Week4TestLogger:
    """Test logging for Week 4"""
    
    def __init__(self, test_suite_name: str):
        self.test_suite_name = test_suite_name
        self.current_test = None
        self.current_category = None
        self.logs = []
        
    def start_test_session(self, session_name: str) -> None:
        """Start test session"""
        self.log_info(f"Starting test session: {session_name}")
    
    def start_test_category(self, category_name: str) -> None:
        """Start test category"""
        self.current_category = category_name
        self.log_info(f"Starting test category: {category_name}")
    
    def end_test_category(self, category_name: str, results: Dict[str, Any]) -> None:
        """End test category"""
        passed = len([r for r in results.values() if r.get("status") == "PASS"])
        total = len(results)
        self.log_info(f"Test category complete: {category_name} - {passed}/{total} passed")
    
    def start_test(self, test_name: str) -> None:
        """Start individual test"""
        self.current_test = test_name
        self.log_info(f"Starting test: {test_name}")
    
    def log_info(self, message: str) -> None:
        """Log info message"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] INFO: {message}"
        self.logs.append(log_entry)
        logger.info(message)
    
    def log_success(self, test_name: str, message: str = "") -> None:
        """Log successful test"""
        msg = f"✅ {test_name} PASSED"
        if message:
            msg += f" - {message}"
        self.log_info(msg)
    
    def log_error(self, test_name: str, error: str) -> None:
        """Log error"""
        msg = f"❌ {test_name} FAILED - {error}"
        self.log_info(msg)
    
    def log_warning(self, message: str, details: str = "") -> None:
        """Log warning"""
        msg = f"⚠️  WARNING: {message}"
        if details:
            msg += f" - {details}"
        self.log_info(msg)
    
    def get_logs(self) -> list:
        """Get all logs"""
        return self.logs.copy()