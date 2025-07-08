"""
Testes completos para worker_factory.py para atingir 100% de cobertura.
"""

import pytest
from app.worker.worker_factory import (
    WorkerInfo, 
    WorkerDefinition, 
    WorkerFactory, 
    worker_factory
)


class TestWorkerInfo:
    """Testes para a classe WorkerInfo"""
    
    def test_worker_info_with_name_only(self):
        """Testa criação de WorkerInfo apenas com name"""
        info = WorkerInfo("test_worker")
        assert info.name == "test_worker"
        assert info.description == ""
    
    def test_worker_info_with_name_and_description(self):
        """Testa criação de WorkerInfo com name e description"""
        info = WorkerInfo("test_worker", "Test description")
        assert info.name == "test_worker"
        assert info.description == "Test description"
    
    def test_worker_info_with_none_description(self):
        """Testa criação de WorkerInfo com description None"""
        info = WorkerInfo("test_worker", None)
        assert info.name == "test_worker"
        assert info.description == ""


class TestWorkerDefinition:
    """Testes para a classe WorkerDefinition"""
    
    def test_worker_definition_basic(self):
        """Testa criação básica de WorkerDefinition"""
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info)
        assert definition.info is info
        assert definition.config == {}
    
    def test_worker_definition_with_config(self):
        """Testa criação de WorkerDefinition com configuração"""
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info, param1="value1", param2="value2")
        assert definition.info is info
        assert definition.config == {"param1": "value1", "param2": "value2"}
    
    def test_worker_definition_with_complex_config(self):
        """Testa criação de WorkerDefinition com configuração complexa"""
        info = WorkerInfo("test_worker", "Complex worker")
        definition = WorkerDefinition(
            info,
            timeout=30,
            retries=3,
            queue="high_priority",
            config_dict={"nested": {"key": "value"}}
        )
        assert definition.info is info
        assert definition.config["timeout"] == 30
        assert definition.config["retries"] == 3
        assert definition.config["queue"] == "high_priority"
        assert definition.config["config_dict"] == {"nested": {"key": "value"}}


class TestWorkerFactory:
    """Testes para a classe WorkerFactory"""
    
    def test_worker_factory_initialization(self):
        """Testa inicialização da WorkerFactory"""
        factory = WorkerFactory()
        assert factory._workers == {}
        assert factory.list_workers() == {}
    
    def test_register_worker(self):
        """Testa registro de um worker"""
        factory = WorkerFactory()
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info)
        
        factory.register("test_worker", definition)
        
        assert "test_worker" in factory._workers
        assert factory._workers["test_worker"] is definition
    
    def test_register_multiple_workers(self):
        """Testa registro de múltiplos workers"""
        factory = WorkerFactory()
        
        info1 = WorkerInfo("worker1")
        definition1 = WorkerDefinition(info1)
        
        info2 = WorkerInfo("worker2")
        definition2 = WorkerDefinition(info2)
        
        factory.register("worker1", definition1)
        factory.register("worker2", definition2)
        
        assert len(factory._workers) == 2
        assert factory._workers["worker1"] is definition1
        assert factory._workers["worker2"] is definition2
    
    def test_create_existing_worker(self):
        """Testa criação de worker existente"""
        factory = WorkerFactory()
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info)
        
        factory.register("test_worker", definition)
        result = factory.create("test_worker")
        
        assert result is definition
    
    def test_create_nonexistent_worker(self):
        """Testa criação de worker inexistente"""
        factory = WorkerFactory()
        result = factory.create("nonexistent_worker")
        assert result is None
    
    def test_list_workers_empty(self):
        """Testa listagem de workers quando vazia"""
        factory = WorkerFactory()
        workers = factory.list_workers()
        assert workers == {}
    
    def test_list_workers_with_workers(self):
        """Testa listagem de workers com workers registrados"""
        factory = WorkerFactory()
        
        info1 = WorkerInfo("worker1")
        definition1 = WorkerDefinition(info1)
        
        info2 = WorkerInfo("worker2")
        definition2 = WorkerDefinition(info2)
        
        factory.register("worker1", definition1)
        factory.register("worker2", definition2)
        
        workers = factory.list_workers()
        assert len(workers) == 2
        assert workers["worker1"] is definition1
        assert workers["worker2"] is definition2
    
    def test_list_workers_returns_copy(self):
        """Testa se list_workers retorna uma cópia"""
        factory = WorkerFactory()
        
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info)
        factory.register("test_worker", definition)
        
        workers1 = factory.list_workers()
        workers2 = factory.list_workers()
        
        # Deve ser diferentes objetos (cópias)
        assert workers1 is not workers2
        assert workers1 == workers2
        
        # Modificar a cópia não deve afetar o original
        workers1["new_worker"] = WorkerDefinition(WorkerInfo("new"))
        assert "new_worker" not in factory._workers
    
    def test_register_override_existing_worker(self):
        """Testa sobrescrever worker existente"""
        factory = WorkerFactory()
        
        info1 = WorkerInfo("worker1", "Original")
        definition1 = WorkerDefinition(info1)
        
        info2 = WorkerInfo("worker1", "Override")
        definition2 = WorkerDefinition(info2)
        
        factory.register("worker1", definition1)
        factory.register("worker1", definition2)
        
        assert factory._workers["worker1"] is definition2
        assert factory._workers["worker1"].info.description == "Override"


class TestGlobalWorkerFactory:
    """Testes para a instância global worker_factory"""
    
    def test_global_worker_factory_exists(self):
        """Testa se a instância global existe"""
        assert worker_factory is not None
        assert isinstance(worker_factory, WorkerFactory)
    
    def test_global_worker_factory_functionality(self):
        """Testa funcionalidade da instância global"""
        # Salvar estado inicial
        initial_workers = worker_factory.list_workers().copy()
        
        # Testar funcionalidade
        info = WorkerInfo("global_test_worker")
        definition = WorkerDefinition(info)
        
        worker_factory.register("global_test_worker", definition)
        
        result = worker_factory.create("global_test_worker")
        assert result is definition
        
        workers = worker_factory.list_workers()
        assert "global_test_worker" in workers
        
        # Limpar teste
        worker_factory._workers.clear()
        worker_factory._workers.update(initial_workers)


class TestWorkerFactoryEdgeCases:
    """Testes de casos extremos"""
    
    def test_register_with_empty_name(self):
        """Testa registro com nome vazio"""
        factory = WorkerFactory()
        info = WorkerInfo("")
        definition = WorkerDefinition(info)
        
        factory.register("", definition)
        
        assert "" in factory._workers
        assert factory.create("") is definition
    
    def test_worker_info_with_special_characters(self):
        """Testa WorkerInfo com caracteres especiais"""
        info = WorkerInfo("worker-with-special_chars@123", "Descrição com acentos çãõ")
        assert info.name == "worker-with-special_chars@123"
        assert info.description == "Descrição com acentos çãõ"
    
    def test_worker_definition_with_none_values(self):
        """Testa WorkerDefinition com valores None"""
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info, param1=None, param2="value")
        
        assert definition.config["param1"] is None
        assert definition.config["param2"] == "value"
    
    def test_factory_create_with_none_name(self):
        """Testa create com nome None"""
        factory = WorkerFactory()
        result = factory.create(None)
        assert result is None
    
    def test_factory_large_number_of_workers(self):
        """Testa factory com grande número de workers"""
        factory = WorkerFactory()
        
        # Registrar 100 workers
        for i in range(100):
            info = WorkerInfo(f"worker_{i}")
            definition = WorkerDefinition(info)
            factory.register(f"worker_{i}", definition)
        
        assert len(factory._workers) == 100
        
        # Testar que todos foram registrados corretamente
        for i in range(100):
            result = factory.create(f"worker_{i}")
            assert result is not None
            assert result.info.name == f"worker_{i}"
        
        # Testar listagem
        workers = factory.list_workers()
        assert len(workers) == 100
