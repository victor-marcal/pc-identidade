"""
Testes completos para o módulo __init__.py do worker.
"""

import pytest
from app.worker import WorkerDefinition, WorkerFactory, WorkerInfo
from app.worker.worker_factory import WorkerDefinition as OriginalWorkerDefinition
from app.worker.worker_factory import WorkerFactory as OriginalWorkerFactory
from app.worker.worker_factory import WorkerInfo as OriginalWorkerInfo


class TestWorkerImports:
    """Testes para importações do módulo worker"""
    
    def test_worker_info_import(self):
        """Testa se WorkerInfo é importado corretamente"""
        assert WorkerInfo is OriginalWorkerInfo
        
        # Teste funcionalidade básica
        info = WorkerInfo("test_worker")
        assert info.name == "test_worker"
        assert info.description == ""
    
    def test_worker_definition_import(self):
        """Testa se WorkerDefinition é importado corretamente"""
        assert WorkerDefinition is OriginalWorkerDefinition
        
        # Teste funcionalidade básica
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info)
        assert definition.info is info
        assert definition.config == {}
    
    def test_worker_factory_import(self):
        """Testa se WorkerFactory é importado corretamente"""
        assert WorkerFactory is OriginalWorkerFactory
        
        # Teste funcionalidade básica
        factory = WorkerFactory()
        assert factory._workers == {}
    
    def test_all_exports(self):
        """Testa se __all__ contém todas as exportações"""
        from app.worker import __all__
        
        expected_exports = ["WorkerDefinition", "WorkerFactory", "WorkerInfo"]
        assert set(__all__) == set(expected_exports)
    
    def test_all_exports_are_importable(self):
        """Testa se todos os itens em __all__ são importáveis"""
        from app.worker import __all__
        import app.worker
        
        for export in __all__:
            assert hasattr(app.worker, export)
            assert getattr(app.worker, export) is not None
    
    def test_worker_integration(self):
        """Testa integração entre as classes importadas"""
        # Criar instâncias usando as classes importadas
        info = WorkerInfo("integration_test", "Integration test worker")
        definition = WorkerDefinition(info, param1="value1")
        factory = WorkerFactory()
        
        # Registrar e criar worker
        factory.register("integration_test", definition)
        result = factory.create("integration_test")
        
        assert result is definition
        assert result.info.name == "integration_test"
        assert result.info.description == "Integration test worker"
        assert result.config["param1"] == "value1"
    
    def test_worker_module_structure(self):
        """Testa estrutura do módulo worker"""
        import app.worker
        
        # Verificar se as classes existem no módulo
        assert hasattr(app.worker, 'WorkerInfo')
        assert hasattr(app.worker, 'WorkerDefinition')
        assert hasattr(app.worker, 'WorkerFactory')
        
        # Verificar se são callables
        assert callable(app.worker.WorkerInfo)
        assert callable(app.worker.WorkerDefinition)
        assert callable(app.worker.WorkerFactory)
    
    def test_worker_class_instantiation(self):
        """Testa instanciação das classes através do módulo"""
        import app.worker
        
        # Instanciar através do módulo
        info = app.worker.WorkerInfo("module_test")
        definition = app.worker.WorkerDefinition(info)
        factory = app.worker.WorkerFactory()
        
        # Verificar instâncias
        assert isinstance(info, app.worker.WorkerInfo)
        assert isinstance(definition, app.worker.WorkerDefinition)
        assert isinstance(factory, app.worker.WorkerFactory)
        
        # Verificar funcionalidade
        assert info.name == "module_test"
        assert definition.info is info
        assert hasattr(factory, '_workers')
    
    def test_worker_module_docstring(self):
        """Testa se o módulo possui estrutura adequada"""
        import app.worker
        
        # Verificar se existe __all__
        assert hasattr(app.worker, '__all__')
        assert isinstance(app.worker.__all__, list)
        assert len(app.worker.__all__) > 0


def test_worker_module_structure():
    """Test that worker module structure is defined."""
    import app.worker
    from app.worker import WorkerDefinition, WorkerFactory, WorkerInfo
    
    # Test that classes are available
    assert WorkerDefinition is not None
    assert WorkerFactory is not None  
    assert WorkerInfo is not None
    
    # Test basic functionality
    info = WorkerInfo("test_worker", "Test worker description")
    assert info.name == "test_worker"
    assert info.description == "Test worker description"
    
    definition = WorkerDefinition(info)
    assert definition.info == info
    
    factory = WorkerFactory()
    factory.register("test", definition)
    assert factory.create("test") == definition
    
    # Test that module exists and has __all__ defined
    assert hasattr(app.worker, '__all__')
    expected_exports = ["WorkerDefinition", "WorkerFactory", "WorkerInfo"]
    assert app.worker.__all__ == expected_exports
