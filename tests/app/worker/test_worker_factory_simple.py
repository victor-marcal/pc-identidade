"""
Testes simples para melhorar cobertura de worker_factory.py
"""

import pytest
from app.worker.worker_factory import WorkerInfo, WorkerDefinition, WorkerFactory, worker_factory


class TestWorkerInfo:
    """Testes para WorkerInfo"""

    def test_worker_info_creation(self):
        """Testa criação de WorkerInfo"""
        info = WorkerInfo("test_worker")
        assert info.name == "test_worker"
        assert info.description == ""

    def test_worker_info_with_description(self):
        """Testa criação de WorkerInfo com descrição"""
        info = WorkerInfo("test_worker", "Test description")
        assert info.name == "test_worker"
        assert info.description == "Test description"


class TestWorkerDefinition:
    """Testes para WorkerDefinition"""

    def test_worker_definition_creation(self):
        """Testa criação de WorkerDefinition"""
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info)
        assert definition.info == info
        assert definition.config == {}

    def test_worker_definition_with_config(self):
        """Testa criação de WorkerDefinition com configuração"""
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info, param1="value1", param2="value2")
        assert definition.info == info
        assert definition.config == {"param1": "value1", "param2": "value2"}


class TestWorkerFactory:
    """Testes para WorkerFactory"""

    def test_worker_factory_creation(self):
        """Testa criação do WorkerFactory"""
        factory = WorkerFactory()
        assert isinstance(factory._workers, dict)
        assert len(factory._workers) == 0

    def test_register_worker(self):
        """Testa registro de worker"""
        factory = WorkerFactory()
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info)
        
        factory.register("test_worker", definition)
        assert "test_worker" in factory._workers
        assert factory._workers["test_worker"] == definition

    def test_create_existing_worker(self):
        """Testa criação de worker existente"""
        factory = WorkerFactory()
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info)
        
        factory.register("test_worker", definition)
        result = factory.create("test_worker")
        assert result == definition

    def test_create_nonexistent_worker(self):
        """Testa criação de worker inexistente"""
        factory = WorkerFactory()
        result = factory.create("nonexistent_worker")
        assert result is None

    def test_list_workers_empty(self):
        """Testa listagem de workers vazia"""
        factory = WorkerFactory()
        workers = factory.list_workers()
        assert workers == {}

    def test_list_workers_with_data(self):
        """Testa listagem de workers com dados"""
        factory = WorkerFactory()
        info1 = WorkerInfo("worker1")
        info2 = WorkerInfo("worker2")
        def1 = WorkerDefinition(info1)
        def2 = WorkerDefinition(info2)
        
        factory.register("worker1", def1)
        factory.register("worker2", def2)
        
        workers = factory.list_workers()
        assert len(workers) == 2
        assert "worker1" in workers
        assert "worker2" in workers
        assert workers["worker1"] == def1
        assert workers["worker2"] == def2

    def test_list_workers_returns_copy(self):
        """Testa que list_workers retorna uma cópia"""
        factory = WorkerFactory()
        info = WorkerInfo("test_worker")
        definition = WorkerDefinition(info)
        factory.register("test_worker", definition)
        
        workers1 = factory.list_workers()
        workers2 = factory.list_workers()
        
        # Deve retornar objetos diferentes (cópias)
        assert workers1 is not workers2
        # Mas com o mesmo conteúdo
        assert workers1 == workers2


class TestGlobalWorkerFactory:
    """Testes para a instância global do worker factory"""

    def test_global_worker_factory_exists(self):
        """Testa que a instância global existe"""
        assert worker_factory is not None
        assert isinstance(worker_factory, WorkerFactory)

    def test_global_worker_factory_functionality(self):
        """Testa funcionalidade da instância global"""
        # Limpa qualquer estado anterior
        worker_factory._workers.clear()
        
        info = WorkerInfo("global_test_worker")
        definition = WorkerDefinition(info)
        
        worker_factory.register("global_test_worker", definition)
        result = worker_factory.create("global_test_worker")
        assert result == definition
        
        # Limpa após o teste
        worker_factory._workers.clear()
