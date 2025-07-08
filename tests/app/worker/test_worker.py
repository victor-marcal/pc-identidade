import pytest


def test_worker_module_import_attempt():
    """Test worker module import behavior"""
    # Agora que worker_factory existe, deveria importar com sucesso
    from app.worker import WorkerDefinition, WorkerFactory, WorkerInfo
    
    assert WorkerDefinition is not None
    assert WorkerFactory is not None
    assert WorkerInfo is not None


def test_worker_module_exists():
    """Test that worker module exists and imports successfully"""
    import app.worker
    
    # O módulo deve existir e ter os atributos esperados
    assert hasattr(app.worker, 'WorkerDefinition')
    assert hasattr(app.worker, 'WorkerFactory')
    assert hasattr(app.worker, 'WorkerInfo')


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


def test_worker_factory_global_instance():
    """Test that the global worker_factory instance is available"""
    from app.worker.worker_factory import worker_factory
    
    assert worker_factory is not None
    from app.worker.worker_factory import WorkerFactory
    assert isinstance(worker_factory, WorkerFactory)
    
    # Test that it has the expected methods
    assert hasattr(worker_factory, 'list_workers')
    assert hasattr(worker_factory, 'register')
    assert hasattr(worker_factory, 'create')
    
    # Test list_workers specifically to cover the missing line
    workers = worker_factory.list_workers()
    assert isinstance(workers, dict)