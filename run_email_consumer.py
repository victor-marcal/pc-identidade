import sys
import os

# Adicionar o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.seller_email_consumer import main

if __name__ == "__main__":
    main()
