import pytest
from app import paths


class TestSellerPaths:
    """Testes para as constantes de rotas do Seller"""
    
    def test_seller_base_path(self):
        """Testa a rota base do seller"""
        assert paths.SELLER_BASE == "/seller/v1/sellers"
    
    def test_seller_get_by_id_path(self):
        """Testa a rota de busca por ID"""
        assert paths.SELLER_GET_BY_ID == "/seller/v1/sellers/buscar"
    
    def test_seller_create_path(self):
        """Testa a rota de criação"""
        assert paths.SELLER_CREATE == "/seller/v1/sellers"
    
    def test_all_paths_are_strings(self):
        """Testa se todas as constantes são strings"""
        assert isinstance(paths.SELLER_BASE, str)
        assert isinstance(paths.SELLER_GET_BY_ID, str)
        assert isinstance(paths.SELLER_CREATE, str)
    
    def test_paths_start_with_slash(self):
        """Testa se todas as rotas começam com barra"""
        assert paths.SELLER_BASE.startswith("/")
        assert paths.SELLER_GET_BY_ID.startswith("/")
        assert paths.SELLER_CREATE.startswith("/")
    
    def test_paths_contain_version(self):
        """Testa se todas as rotas contêm versão v1"""
        assert "v1" in paths.SELLER_BASE
        assert "v1" in paths.SELLER_GET_BY_ID
        assert "v1" in paths.SELLER_CREATE
    
    def test_module_constants_exist(self):
        """Testa se o módulo exporta as constantes esperadas"""
        expected_constants = [
            'SELLER_BASE',
            'SELLER_GET_BY_ID', 
            'SELLER_CREATE'
        ]
        
        for constant in expected_constants:
            assert hasattr(paths, constant), f"Constante {constant} não encontrada"
    
    def test_paths_consistency(self):
        """Testa consistência entre as rotas"""
        # Todas as rotas devem começar com o mesmo prefixo base
        base_prefix = "/seller/v1"
        assert paths.SELLER_BASE.startswith(base_prefix)
        assert paths.SELLER_GET_BY_ID.startswith(base_prefix)
        assert paths.SELLER_CREATE.startswith(base_prefix)
