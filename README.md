# pc-identidade

## 📌 Identidade do Varejista

O projeto pc-identidade é responsável por estruturar e definir quem é o varejista dentro do sistema do marketplace. A proposta é identificar, validar e organizar as informações que permitem que o varejista seja reconhecido, aprovado e integrado com segurança e clareza ao ecossistema do marketplace.
Esta camada de identidade será essencial para garantir a confiabilidade dos vendedores na plataforma, atender requisitos legais, e oferecer um processo de onboarding eficiente.

[Documentação do Projeto](https://docs.google.com/document/d/11eIj0-f68q7rLtMQsC7VShPTmDfvgnPDPt6HPMMM_Z4/edit?tab=t.0#heading=h.4bbpjvh4rnth)

## 🎯 Objetivos principais:
- Identificação e validação da identidade do varejista
- Recolhimento e análise de dados/documentos obrigatórios
- Organização das informações operacionais e de negócio
- Preparação dos dados para uso nas demais áreas do marketplace

## 👥 Participantes do Time:

- João Pedro
- Marcella Palazzo
- Murilo Alves
- Victor Hugo Buiatti

---

## 🐳 Instalação do Docker

Para instalação do [Docker](https://docs.docker.com/engine/install/ubuntu/), siga o manual disponível no site oficial.

## 🚀 Ambiente de Desenvolvimento Local (Windows)

Este guia descreve o fluxo de trabalho para rodar os serviços de apoio (MongoDB, Keycloak, etc.) via Docker, e a aplicação FastAPI localmente na sua máquina.

### Pré-requisitos
- **Git**
- **Python 3.12**
- **Docker Desktop** para Windows (instalado e em execução)

### Passo 1: Preparar o Projeto

1.  **Clone o Repositório:** Se ainda não o fez, clone o projeto.
    ```powershell
    git clone [https://github.com/projeto-carreira-luizalabs-2025/pc-identidade.git](https://github.com/projeto-carreira-luizalabs-2025/pc-identidade.git)
    ```

2.  **Acesse a Pasta do Projeto:**
    ```powershell
    cd pc-identidade
    ```

### Passo 2: Configurar Variáveis de Ambiente (`.env`)

Crie um arquivo chamado `.env` na raiz do projeto. Ele é crucial para a comunicação da sua aplicação com os serviços no Docker.

**Copie e cole o seguinte conteúdo nele:**
```env
# Variáveis de Ambiente Globais
ENV=dev

# --- Banco de Dados Quente (Principal) ---
# Conexão com autenticação.
APP_DB_URL_MONGO=mongodb://admin:admin@localhost:27017/bd01?authSource=admin
MONGO_DB=pc_identidade

# --- Banco de Dados Frio (Arquivo de Inativos) ---
# Conexão com autenticação.
MONGO_COLD_URL=mongodb://admin_cold:admin_cold@localhost:27018/bd01_cold?authSource=admin

# --- Keycloak ---
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM_NAME=marketplace
KEYCLOAK_CLIENT_ID=varejo
KEYCLOAK_WELL_KNOWN_URL=http://localhost:8080/realms/marketplace/.well-known/openid-configuration

# Credenciais Admin do Keycloak
KEYCLOAK_ADMIN_USER=admin_marketplace
KEYCLOAK_ADMIN_PASSWORD=senha123
KEYCLOAK_ADMIN_CLIENT_ID=admin-cli

# --- Logging ---
PC_LOGGING_LEVEL=info
PC_LOGGING_ENV=dev

# --- RabbitMQ ---
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=admin
RABBITMQ_EXCHANGE=data_exchange
RABBITMQ_QUEUE=data_queue
RABBITMQ_ROUTING_KEY=

# --- Email (Exemplo) ---
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=joaopedrovr91@gmail.com
SENDER_PASSWORD=nmfi fekq qvob jgnv
```

### Passo 3: Preparar Ambiente Python

1. **Crie o ambiente virtual (execute apenas uma vez):**

```powershell
python -m venv venv
```

2. **Ative o ambiente virtual (execute sempre que for desenvolver):**

```powershell
.\venv\Scripts\activate
```

3. **Instale as dependências:**

```powershell
pip install -r requirements.txt
```

### Passo 4: Iniciar os Serviços no Docker

Este comando irá subir os contêineres do MongoDB (quente e frio), Keycloak e RabbitMQ.

```powershell
docker-compose up --build -d
```

Aguarde de 1 a 2 minutos para que os serviços iniciem completamente.

### Passo 5: Configurar o Keycloak (Passo Crítico Pós-Inicialização)

Após os contêineres estarem no ar, você precisa executar o script abaixo para configurar corretamente os atributos de usuário no Keycloak.

```powershell
# Com o venv ativado
python devtools/keycloak-config/setup_sellers_attribute.py
```

### Passo 6: Executar a Aplicação FastAPI

Com tudo pronto, inicie o servidor da sua aplicação localmente (garanta que o venv está ativado).

```powershell
uvicorn app.api_main:app --reload --port 8000
```

### Acessando os Serviços

- API (Swagger UI): http://127.0.0.1:8000/api/docs
- Admin Console do Keycloak: http://localhost:8080
  - **Usuário**: admin
  - **Senha**: admin
- RabbitMQ Management: http://localhost:15672

---

## 🛠️ Tarefas de Manutenção e Scripts

Execute estes scripts no seu terminal com o ambiente virtual (venv) ativado.

### Arquivando Sellers Inativos (Banco Frio)

Para mover todos os sellers com status "Inativo" do banco de dados principal para o banco de dados de arquivamento (frio), execute:

```powershell
python devtools/scripts/move_inactive_to_cold.py
```

## 🔍 Análise de Qualidade com SonarQube

Para subir o ambiente do SonarQube com Docker Compose, execute:

``` bash
make docker-compose-sonar-up # Inicia o servidor SonarQube e seus serviços dependentes (como o banco de dados) via Docker Compose
```

Após a execução, acesse a interface web do SonarQube em: http://localhost:9000

Se em algum momento quiser parar o ambiente do SonarQube, execute:

```bash
make docker-compose-sonar-down # Desligará o ambiente do SonarQube e removerá os contêineres
```

### 1. Gere e exporte o token do SonarQube
Após acessar o SonarQube:

* **Vá em "My Account" > "Security".**

* **Gere um novo token (ex: pc-identidade-token).**

* **No terminal, exporte o token:**

```
export SONAR_TOKEN=<seu_token_aqui>
export SONAR_HOST_URL=http://localhost:9000 pysonar-scanner
```

### Windows 🖥️

1. Baixar o Sonar Scanner

🔗 Link oficial

Acesse: https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/scanners/sonarscanner/

Clique em Download the SonarScanner.

Baixe o arquivo .zip para Windows (ex: sonar-scanner-cli-5.x.x-windows.zip).

Extraia para um local como: C:\sonar-scanner\

2. Configurar Variáveis de Ambiente ✅ 

🔧 Adicionar ao PATH:

Abra o menu Iniciar e digite "variáveis de ambiente".

Clique em "Editar variáveis de ambiente do sistema".

Em Variáveis de Sistema, clique em Path > Editar > Novo e adicione:

```
C:\sonar-scanner\bin
```
Clique em OK para fechar tudo.

para rodar no projeto e apenas digitar no terminal 
```
sonar-scanner 
```

Isso irá enviar os dados da sua aplicação para análise no SonarQube.


No windows é necessário configurar o token e host_url:
```
$env:SONAR_HOST_URL = "http://localhost:9000"
$env:SONAR_TOKEN = "seu-token"
```

3. Execute o Sonar Scanner

Com os containers rodando e o token configurado, execute:

```
SONAR_HOST_URL=http://localhost:9000 pysonar-scanner
```

## 📄 Sistema de Migrations para MongoDB

O projeto utiliza um sistema de migrations para gerenciar mudanças no esquema do banco de dados MongoDB de forma organizada e versionada.

### 🚀 Como criar uma nova migration

Você pode criar uma nova migration de duas formas:

**Opção 1 - Usando o comando original da biblioteca:**
```bash
mongodb-migrate-create --description "adicionar campo status na collection users"
```

**Opção 2 - Usando o comando do Makefile (recomendado):**
```bash
make migration-create NOME="adicionar campo status na collection users"
```

Ambos os comandos criarão um arquivo de migration na pasta `migrations/` com timestamp e descrição.

### ▶️ Como executar as migrations

Para aplicar todas as migrations pendentes, você pode usar:

**Opção 1 - Usando o comando do Makefile (recomendado):**
```bash
make migration-run
```

**Opção 2 - Executando diretamente o script:**
```bash
python3.12 run_migrations.py
```

### 🔧 Configuração

As migrations utilizam a mesma configuração de banco definida nas variáveis de ambiente do projeto (`APP_DB_URL_MONGO`).


### Comandos Úteis do Dia a Dia

Para ver os logs da aplicação em tempo real:

```bash
docker-compose logs -f app
```

Para parar todos os serviços:

```bash
docker-compose down
```

Para iniciar os serviços novamente (sem reconstruir):

```bash
docker-compose up -d
```

Para testar se o Mongo está acessível

Em outro terminal, rode:

```bash
docker run --rm -it mongo mongosh "mongodb://admin:admin@pc-identidade-mongo:27017/bd01?authSource=admin"
```

Você verá o prompt bd01> se tudo estiver OK.