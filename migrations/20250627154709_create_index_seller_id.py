from mongodb_migrations.base import BaseMigration


from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    def upgrade(self):
        """
        Criar índice no campo seller_id para melhorar performance das consultas
        """
        sellers_collection = self.db['sellers']
        sellers_collection.create_index("seller_id", unique=True)

    def downgrade(self):
        """
        Remover o índice do seller_id (rollback)
        """
        sellers_collection = self.db['sellers']
        sellers_collection.drop_index("seller_id")
