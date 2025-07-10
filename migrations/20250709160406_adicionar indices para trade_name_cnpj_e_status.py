from mongodb_migrations.base import BaseMigration
import pymongo


class Migration(BaseMigration):
    def upgrade(self):
        """
        Adiciona índices para trade_name (nome_fantasia), cnpj e o índice composto
        de status e created_at para otimizar as buscas.
        """
        # Obtém a coleção 'sellers'
        sellers_collection = self.db['sellers']

        print("\nCriando índice único para 'trade_name'...")
        sellers_collection.create_index("trade_name", unique=True)
        print("Índice para 'trade_name' criado com sucesso.")

        print("Criando índice para 'cnpj'...")
        sellers_collection.create_index("cnpj")
        print("Índice para 'cnpj' criado com sucesso.")

        print("Criando índice composto para 'status' e 'created_at'...")
        sellers_collection.create_index(
            [("status", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)]
        )
        print("Índice composto criado com sucesso.")

    def downgrade(self):
        """
        Remove os índices de trade_name, cnpj e o composto de status. (Rollback)
        """
        sellers_collection = self.db['sellers']

        print("\nRemovendo índice de 'trade_name'...")
        sellers_collection.drop_index("trade_name_1")
        print("Índice de 'trade_name' removido.")

        print("Removendo índice de 'cnpj'...")
        sellers_collection.drop_index("cnpj_1")
        print("Índice de 'cnpj' removido.")

        print("Removendo índice composto de 'status' e 'created_at'...")
        sellers_collection.drop_index("status_1_created_at_-1")
        print("Índice composto removido.")
