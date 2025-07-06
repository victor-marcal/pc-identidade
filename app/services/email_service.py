import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List


class EmailService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.server = os.getenv("SMTP_SERVER")
        self.port = os.getenv("SMTP_PORT")
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.password = os.getenv("SENDER_PASSWORD")

    def send_welcome_email(self, seller_data: Dict):
        """
        Envia email de boas-vindas para o seller
        """
        try:
            # Extrair dados do seller
            company_name = seller_data.get("company_name", "Nova Empresa")
            trade_name = seller_data.get("trade_name", "")
            business_description = seller_data.get("business_description", "")
            product_categories = seller_data.get("product_categories", [])
            contact_email = seller_data.get("contact_email", "")
            
            if not contact_email:
                self.logger.error("Email de contato não encontrado nos dados do seller")
                return False

            # Criar o corpo do email
            body = self._create_welcome_email_body(
                company_name, trade_name, business_description, product_categories
            )
            
            # Configurar mensagem
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = contact_email
            message['Subject'] = f"Bem-vindo(a) {company_name}!"
            message.attach(MIMEText(body, 'html'))

            # Enviar email
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, contact_email, message.as_string())

            self.logger.info(f"Email de boas-vindas enviado com sucesso para {contact_email}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao enviar email de boas-vindas: {str(e)}")
            return False

    def _create_welcome_email_body(self, company_name: str, trade_name: str, 
                                   business_description: str, product_categories: List[str]) -> str:
        """
        Cria o corpo HTML do email de boas-vindas
        """
        # Formatar categorias de produtos
        categories_html = ""
        if product_categories:
            categories_list = "</li><li>".join(product_categories)
            categories_html = f"""
            <div style="margin: 20px 0;">
                <h3 style="color: #2c5aa0; margin-bottom: 10px;">Categorias de Produtos:</h3>
                <ul style="margin-left: 20px;">
                    <li>{categories_list}</li>
                </ul>
            </div>
            """

        # Nome da empresa para exibição
        display_name = f"{company_name}"
        if trade_name and trade_name != company_name:
            display_name = f"{company_name} ({trade_name})"

        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bem-vindo ao Marketplace!</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f5f5f5;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5;">
                <tr>
                    <td align="center" style="padding: 40px 0;">
                        <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <tr>
                                <td style="padding: 40px 30px; text-align: center;">
                                    <div style="margin-bottom: 30px;">
                                        <h1 style="color: #2c5aa0; margin: 0; font-size: 28px;">🎉 Bem-vindo(a) ao nosso Marketplace!</h1>
                                    </div>
                                    
                                    <div style="text-align: left; margin: 30px 0;">
                                        <h2 style="color: #333; margin-bottom: 15px;">Olá, {display_name}!</h2>
                                        
                                        <p style="color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
                                            É com grande satisfação que damos as boas-vindas à sua empresa em nossa plataforma! 
                                            Estamos empolgados em ter você como nosso novo parceiro.
                                        </p>

                                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                            <h3 style="color: #2c5aa0; margin-bottom: 10px;">Sobre seu negócio:</h3>
                                            <p style="color: #555; font-size: 15px; line-height: 1.5; margin: 0;">
                                                {business_description}
                                            </p>
                                        </div>

                                        {categories_html}

                                        <div style="margin: 30px 0;">
                                            <p style="color: #666; font-size: 16px; line-height: 1.6;">
                                                Nossa equipe está à disposição para auxiliá-lo em qualquer dúvida ou necessidade. 
                                                Juntos, vamos alcançar grandes resultados!
                                            </p>
                                        </div>

                                        <div style="text-align: center; margin-top: 30px;">
                                            <div style="background-color: #2c5aa0; color: white; padding: 15px 30px; border-radius: 5px; display: inline-block;">
                                                <strong>Obrigado por fazer parte da nossa comunidade!</strong>
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; border-radius: 0 0 10px 10px;">
                                    <p style="color: #888; font-size: 14px; margin: 0;">
                                        Este é um email automático de boas-vindas. Para suporte, entre em contato conosco.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
