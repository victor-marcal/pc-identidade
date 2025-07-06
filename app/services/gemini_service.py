import logging
import os
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


class GeminiService:
    """Serviço principal para chat com IA Gemini - mantém funcionalidade original."""
    
    def __init__(self, api_key: str, pdfs_folder_path: str = "pdfs"):
        self.api_key = api_key
        self.pdfs_folder_path = pdfs_folder_path
        self.pdf_content: Optional[str] = None
        self.memory = ConversationBufferWindowMemory(
            k=5, return_messages=True, memory_key="chat_history", output_key="output"
        )
        self.chain = None
        self._initialize()

    def _initialize(self):
        """Inicializa o serviço carregando PDFs e criando a chain."""
        self.pdf_content = self._load_pdfs_from_folder()
        if not self.pdf_content:
            raise ValueError("Não foi possível carregar os documentos PDF.")
        self.chain = self._create_chain()

    def _load_pdfs_from_folder(self) -> str:
        """Carrega todos os PDFs de uma pasta e retorna o conteúdo como texto."""
        try:
            pasta = Path(self.pdfs_folder_path)
            if not pasta.exists():
                logger.warning(f"Pasta {self.pdfs_folder_path} não encontrada.")
                return ""
            
            conteudo_total = ""
            pdf_files = list(pasta.glob("*.pdf"))
            
            if not pdf_files:
                logger.warning(f"Nenhum arquivo PDF encontrado na pasta {self.pdfs_folder_path}.")
                return ""
            
            for pdf_file in pdf_files:
                try:
                    doc = fitz.open(str(pdf_file))
                    texto_pdf = ""
                    
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        texto_pdf += page.get_text()
                    
                    doc.close()
                    conteudo_total += f"\n\n--- Conteúdo do arquivo {pdf_file.name} ---\n\n{texto_pdf}"
                    logger.info(f"PDF {pdf_file.name} carregado com sucesso.")
                    
                except Exception as e:
                    logger.error(f"Erro ao processar PDF {pdf_file.name}: {e}")
                    continue
            
            return conteudo_total
        
        except Exception as e:
            logger.error(f"Erro ao carregar PDFs da pasta {self.pdfs_folder_path}: {e}")
            return ""

    def _create_chain(self):
        """Cria a cadeia Langchain para o Gemini."""
        # Escapar chaves do conteúdo PDF para evitar conflitos com template
        escaped_pdf_content = self.pdf_content.replace("{", "{{").replace("}", "}}")

        system_message = f"""Você é um assistente amigável chamado falaSeller, especialista em informações
        do Seller.
        Você possui acesso EXCLUSIVO às seguintes informações vindas de documentos PDF e APENAS esses PDFs:

        ####
        {escaped_pdf_content}
        ####

        Utilize AS INFORMAÇÕES FORNECIDAS ACIMA para basear as suas respostas.  NÃO invente informações ou
        use conhecimento externo.
        Se a resposta não estiver explicitamente nos documentos, diga que você não sabe.

        Sempre que houver $ na sua saída, substita por S.!"""

        template = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("placeholder", "{chat_history}"),
                ("user", "{input}"),
            ]
        )
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", google_api_key=self.api_key
            )
            chain = template | llm
            return chain
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar o modelo de chat Gemini: {e}") from e

    def generate_response(self, user_message: str) -> str:
        """Gera uma resposta usando o modelo Gemini."""
        try:
            response = self.chain.invoke(
                {"input": user_message, "chat_history": self.memory.buffer_as_messages}
            )
            
            # Atualiza o histórico de mensagens
            self.memory.chat_memory.add_user_message(user_message)
            self.memory.chat_memory.add_ai_message(response.content)
            
            return response.content
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com Gemini: {e}")
            raise
    
    def chat(self, message: str) -> str:
        """Método para compatibilidade com o router."""
        return self.generate_response(message)
