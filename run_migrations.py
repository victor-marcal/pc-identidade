#!/usr/bin/env python3
"""
Script para executar todas as migrations automaticamente
"""

import os
import sys
import importlib.util
from pymongo import MongoClient

def get_mongo_url():
    """Pega a URL do MongoDB das variáveis de ambiente ou usa padrão"""
    # Tenta pegar do ambiente, senão usa padrão
    return os.getenv('APP_DB_URL_MONGO', 'mongodb://admin:admin@localhost:27017/bd01?authSource=admin')

def load_migration_module(filepath):
    """Carrega um módulo Python de migration"""
    spec = importlib.util.spec_from_file_location("migration", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_migrations():
    """Execute todas as migrations na pasta migrations/ em sequência"""
    
    # Conectar ao MongoDB
    mongo_url = get_mongo_url()
    client = MongoClient(mongo_url)
    db = client.bd01
    
    print(f"🔗 Conectado ao MongoDB: {mongo_url}")
    print(f"📋 Collections disponíveis: {db.list_collection_names()}")
    
    # Pasta de migrations
    migrations_dir = "migrations"
    
    if not os.path.exists(migrations_dir):
        print(f"❌ Pasta {migrations_dir} não encontrada!")
        return
    
    # Listar arquivos de migration
    migration_files = []
    for filename in os.listdir(migrations_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            migration_files.append(filename)
    
    # Ordenar por timestamp (nome do arquivo)
    migration_files.sort()
    
    if not migration_files:
        print("📁 Nenhuma migration encontrada!")
        return
    
    print(f"📁 Encontradas {len(migration_files)} migrations:")
    for filename in migration_files:
        print(f"  - {filename}")
    
    # Executar cada migration em sequência
    for filename in migration_files:
        filepath = os.path.join(migrations_dir, filename)
        print(f"\n▶️ Executando: {filename}")
        
        try:
            # Carregar o módulo da migration
            module = load_migration_module(filepath)
            
            # Verificar se tem a classe Migration
            if not hasattr(module, 'Migration'):
                print(f"⚠️ Arquivo {filename} não contém classe 'Migration', pulando...")
                continue
            
            # Instanciar a migration
            migration_class = getattr(module, 'Migration')
            
            # Tentar executar diretamente sem a BaseMigration
            try:
                # Criar instância da migration passando db como parâmetro
                migration_instance = migration_class()
                migration_instance.db = db
            except Exception:
                # Se não funcionar, criar uma versão simples
                migration_instance = type('SimpleMigration', (), {'db': db})()
                # Copiar o método upgrade para a instância
                if hasattr(migration_class, 'upgrade'):
                    def make_upgrade(cls, instance):
                        return lambda: cls.upgrade(instance)
                    migration_instance.upgrade = make_upgrade(migration_class, migration_instance)
            
            # Executar o upgrade
            if hasattr(migration_instance, 'upgrade'):
                migration_instance.upgrade()
                print(f"✅ Migration {filename} executada com sucesso!")
            else:
                print(f"⚠️ Migration {filename} não tem método 'upgrade', pulando...")
                
        except Exception as e:
            print(f"❌ Erro ao executar {filename}: {e}")
            import traceback
            traceback.print_exc()
            # Continua para a próxima migration mesmo se uma falhar
    
    client.close()
    print("\n🎉 Todas as migrations foram processadas!")

if __name__ == "__main__":
    run_migrations()