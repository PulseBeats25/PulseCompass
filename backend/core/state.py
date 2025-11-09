"""
Application State Management
Centralized state management to replace app.state pattern
"""
from typing import Dict, Any, Optional
from threading import Lock

class AppState:
    """Thread-safe application state manager"""
    
    def __init__(self):
        self._processed_files: Dict[str, Any] = {}
        self._lock = Lock()
    
    def get_processed_files(self) -> Dict[str, Any]:
        """Get all processed files"""
        with self._lock:
            return self._processed_files.copy()
    
    def get_processed_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific processed file"""
        with self._lock:
            return self._processed_files.get(file_id)
    
    def set_processed_file(self, file_id: str, data: Dict[str, Any]) -> None:
        """Store processed file data"""
        with self._lock:
            self._processed_files[file_id] = data
    
    def delete_processed_file(self, file_id: str) -> bool:
        """Delete a processed file"""
        with self._lock:
            if file_id in self._processed_files:
                del self._processed_files[file_id]
                return True
            return False
    
    def clear_processed_files(self) -> None:
        """Clear all processed files"""
        with self._lock:
            self._processed_files.clear()
    
    def get_files_by_company(self, company_id: str) -> Dict[str, Any]:
        """Get all files for a specific company"""
        with self._lock:
            return {
                k: v for k, v in self._processed_files.items()
                if v.get('company_id') == company_id
            }


# Global state instance
_app_state = AppState()


def get_app_state() -> AppState:
    """Get the global application state"""
    return _app_state


def get_processed_files() -> Dict[str, Any]:
    """Get all processed files"""
    return _app_state.get_processed_files()


def get_processed_file(file_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific processed file"""
    return _app_state.get_processed_file(file_id)


def set_processed_file(file_id: str, data: Dict[str, Any]) -> None:
    """Store processed file data"""
    _app_state.set_processed_file(file_id, data)


def delete_processed_file(file_id: str) -> bool:
    """Delete a processed file"""
    return _app_state.delete_processed_file(file_id)


def clear_processed_files() -> None:
    """Clear all processed files"""
    _app_state.clear_processed_files()


def get_files_by_company(company_id: str) -> Dict[str, Any]:
    """Get all files for a specific company"""
    return _app_state.get_files_by_company(company_id)
