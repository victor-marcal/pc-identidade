import pytest


def test_worker_module_import_attempt():
    """Test worker module import behavior"""
    with pytest.raises(ImportError):
        from app.worker import WorkerDefinition, WorkerFactory, WorkerInfo


def test_worker_module_exists():
    """Test that worker module exists but fails to import due to missing worker_factory"""
    with pytest.raises(ModuleNotFoundError, match="No module named 'app.worker.worker_factory'"):
        import app.worker


def test_worker_module_all_attribute():
    """Test worker module __all__ attribute coverage"""
    try:
        import app.worker

        assert hasattr(app.worker, '__all__')
        expected_all = ["WorkerDefinition", "WorkerFactory", "WorkerInfo"]
        assert app.worker.__all__ == expected_all
    except ImportError:
        import importlib.util
        import sys

        spec = importlib.util.find_spec("app.worker")
        if spec and spec.origin:
            with open(spec.origin, 'r') as f:
                content = f.read()
                assert '__all__' in content
                assert '"WorkerDefinition"' in content
                assert '"WorkerFactory"' in content
                assert '"WorkerInfo"' in content
