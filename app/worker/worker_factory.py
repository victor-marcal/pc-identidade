"""Worker factory definitions."""

from typing import Any, Dict, Optional


class WorkerInfo:
    """Worker information class."""
    
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description or ""


class WorkerDefinition:
    """Worker definition class."""
    
    def __init__(self, info: WorkerInfo, **kwargs):
        self.info = info
        self.config = kwargs


class WorkerFactory:
    """Factory for creating workers."""
    
    def __init__(self):
        self._workers: Dict[str, WorkerDefinition] = {}
    
    def register(self, name: str, definition: WorkerDefinition):
        """Register a worker definition."""
        self._workers[name] = definition
    
    def create(self, name: str) -> Optional[WorkerDefinition]:
        """Create a worker by name."""
        return self._workers.get(name)
    
    def list_workers(self) -> Dict[str, WorkerDefinition]:
        """List all registered workers."""
        return self._workers.copy()


# Global worker factory instance
worker_factory = WorkerFactory()

__all__ = ["WorkerInfo", "WorkerDefinition", "WorkerFactory", "worker_factory"]
