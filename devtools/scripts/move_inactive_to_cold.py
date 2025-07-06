import os
import sys
import asyncio
import logging
from dotenv import load_dotenv


sys.path.append(os.getcwd())

from app.integrations.database.mongo_client import MongoClient
from pclogging import LoggingBuilder

load_dotenv()

# --- INICIALIZAÇÃO DO LOGGING ---
LoggingBuilder.init()
logging.basicConfig(level=LoggingBuilder._log_level)
logger = logging.getLogger(__name__)

# --- Configurações dos Bancos de Dados ---
HOT_DB_URI = os.getenv("APP_DB_URL_MONGO")
COLD_DB_URI = os.getenv("MONGO_COLD_URL")
HOT_DB_NAME = os.getenv("MONGO_DB", "pc_identidade")
COLD_DB_NAME = "bd01_cold"
COLLECTION_NAME = "sellers"


async def migrate_inactive_sellers():
    """
    Conecta aos bancos de dados quente e frio, move os sellers inativos
    do quente para o frio, e os apaga do quente, com logging.
    """
    hot_client = None
    cold_client = None
    try:
        logger.info("Iniciando script de migração de sellers inativos.")
        logger.info("Conectando aos bancos de dados quente e frio...")
        hot_client = MongoClient(HOT_DB_URI)
        cold_client = MongoClient(COLD_DB_URI)

        hot_db = hot_client.get_database(HOT_DB_NAME)
        hot_collection = hot_db[COLLECTION_NAME]

        cold_db = cold_client.get_database(COLD_DB_NAME)
        cold_collection = cold_db[COLLECTION_NAME]

        logger.info("Conexão com os bancos de dados estabelecida com sucesso.")

        inactive_sellers = await hot_collection.find({"status": "Inativo"}).to_list(length=None)

        if not inactive_sellers:
            logger.info("Nenhum seller inativo encontrado. Nenhuma ação necessária.")
            return

        logger.info(f"Encontrados {len(inactive_sellers)} sellers inativos para migrar.")

        for seller in inactive_sellers:
            seller_id = seller.get("seller_id")
            logger.debug(f"Processando seller: {seller_id}...")

            await cold_collection.replace_one({"_id": seller["_id"]}, seller, upsert=True)
            logger.info(f"  -> Seller '{seller_id}' salvo no banco frio.")

            await hot_collection.delete_one({"_id": seller["_id"]})
            logger.info(f"  -> Seller '{seller_id}' removido do banco quente.")

        logger.info("Migração de todos os sellers inativos concluída com sucesso!")

    except Exception as e:
        logger.error("ERRO: Um erro inesperado ocorreu durante a migração.", exc_info=True)
    finally:
        if hot_client:
            hot_client.close()
        if cold_client:
            cold_client.close()
        logger.info("Conexões com os bancos de dados fechadas.")


if __name__ == "__main__":
    asyncio.run(migrate_inactive_sellers())
