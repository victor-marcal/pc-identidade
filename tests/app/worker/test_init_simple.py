"""
Testes simples para melhorar cobertura de worker/__init__.py
"""

import pytest


class TestWorkerInit:
    """Testes para o módulo worker"""

    def test_imports(self):
        """Testa importações do módulo worker"""
        from app.worker import WorkerDefinition, WorkerFactory, WorkerInfo
        
        assert WorkerDefinition is not None
        assert WorkerFactory is not None  
        assert WorkerInfo is not None

    def test_all_exports(self):
        """Testa exports do módulo worker"""
        import app.worker as worker_module
        
        expected_exports = ["WorkerDefinition", "WorkerFactory", "WorkerInfo"]
        assert hasattr(worker_module, '__all__')
        assert worker_module.__all__ == expected_exports

    def test_classes_exist(self):
        """Testa que as classes existem"""
        from app.worker import WorkerDefinition, WorkerFactory, WorkerInfo
        
        # Testa que são classes
        assert callable(WorkerDefinition)
        assert callable(WorkerFactory)
        assert callable(WorkerInfo)

    def test_can_instantiate_classes(self):
        """Testa que as classes podem ser instanciadas"""
        from app.worker import WorkerDefinition, WorkerFactory, WorkerInfo
        
        # Testa WorkerInfo
        info = WorkerInfo("test")
        assert info.name == "test"
        
        # Testa WorkerFactory
        factory = WorkerFactory()
        assert isinstance(factory._workers, dict)
        
        # Testa WorkerDefinition
        definition = WorkerDefinition(info)
        assert definition.info == info
