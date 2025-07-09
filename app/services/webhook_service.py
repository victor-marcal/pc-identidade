import httpx
import logging
from typing import Dict, Any

from app.settings.app import settings
from app.common.datetime import utcnow

logger = logging.getLogger(__name__)

JSON = "application/json"

class WebhookService:
    def __init__(self):
        self.webhook_url = settings.WEBHOOK_URL
        self.timeout = 30.0

    async def send_update_message(self, message: str, changes: Dict[str, Any]) -> bool:
        """
        Envia uma mensagem simples com as alterações feitas.
        
        Args:
            message: Mensagem descritiva do que foi alterado
            changes: Dicionário com as alterações realizadas
        
        Returns:
            bool: True se a mensagem foi enviada com sucesso, False caso contrário
        """
        logger.warning(f"🚀 WEBHOOK: Iniciando envio - {message}")
        
        try:
            # Formato bonito e organizado para Slack
            changes_text = self._format_changes(changes)
            
            # Cores baseadas no tipo de operação
            color_map = {
                "created": "good",      # Verde
                "updated": "warning",   # Amarelo
                "deleted": "danger",    # Vermelho
                "replaced": "#439FE0"   # Azul
            }
            
            operation = changes.get("operation", "updated")
            color = color_map.get(operation, "good")
            
            slack_payload = {
                "text": f"🔔 *{message}*",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {
                                "title": "📋 Detalhes",
                                "value": changes_text,
                                "short": False
                            }
                        ],
                        "footer": "PC Identidade",
                        "ts": int(utcnow().timestamp())
                    }
                ]
            }
            
            logger.warning(f"🔗 WEBHOOK: URL = {self.webhook_url}")
            logger.warning(f"📦 WEBHOOK: Payload = {slack_payload}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=slack_payload,
                    headers={"Content-Type": JSON}
                )
                
                logger.warning(f"📈 WEBHOOK: Status = {response.status_code}")
                logger.warning(f"📄 WEBHOOK: Resposta = {response.text}")
                
                response.raise_for_status()
                logger.warning("✅ WEBHOOK: Mensagem enviada com sucesso!")
                return True
                
        except httpx.TimeoutException:
            logger.error("❌ WEBHOOK: Timeout ao enviar mensagem")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ WEBHOOK: Erro HTTP {e.response.status_code}")
            logger.error(f"❌ WEBHOOK: Resposta do servidor: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ WEBHOOK: Erro inesperado: {str(e)}")
            logger.error(f"❌ WEBHOOK: URL: {self.webhook_url}")
            return False

    def _format_changes(self, changes: Dict[str, Any]) -> str:
        """Formata as alterações de forma mais legível para o Slack"""
        formatted_lines = []
        
        # Emojis para diferentes tipos de operação
        operation_emojis = {
            "created": "✨ Criado",
            "updated": "📝 Atualizado", 
            "deleted": "🗑️ Excluído",
            "replaced": "🔄 Substituído"
        }
        
        # Formatação da operação
        if "operation" in changes:
            operation = changes["operation"]
            emoji_text = operation_emojis.get(operation, f"🔧 {operation.title()}")
            formatted_lines.append(f"*Operação:* {emoji_text}")
        
        # Formatação do seller_id
        if "seller_id" in changes:
            formatted_lines.append(f"*Seller ID:* `{changes['seller_id']}`")
        
        # Formatação dos campos alterados
        if "fields_changed" in changes and changes["fields_changed"]:
            formatted_lines.append("*Campos alterados:*")
            for field, value in changes["fields_changed"].items():
                # Tradução de alguns campos para português
                field_translations = {
                    "trade_name": "Nome Fantasia",
                    "company_name": "Razão Social", 
                    "contact_email": "Email de Contato",
                    "contact_phone": "Telefone de Contato",
                    "cnpj": "CNPJ",
                    "status": "Status"
                }
                field_name = field_translations.get(field, field.replace("_", " ").title())
                formatted_lines.append(f"  • *{field_name}:* {value}")
        
        return "\n".join(formatted_lines)
