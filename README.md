# pc-identidade

## 📌 Identidade do Varejista

O projeto pc-identidade é responsável por estruturar e definir quem é o varejista dentro do sistema do marketplace. A proposta é identificar, validar e organizar as informações que permitem que o varejista seja reconhecido, aprovado e integrado com segurança e clareza ao ecossistema do marketplace.
Esta camada de identidade será essencial para garantir a confiabilidade dos vendedores na plataforma, atender requisitos legais, e oferecer um processo de onboarding eficiente.

[Documentação do Projeto](https://docs.google.com/document/d/11eIj0-f68q7rLtMQsC7VShPTmDfvgnPDPt6HPMMM_Z4/edit?tab=t.0#heading=h.4bbpjvh4rnth)

## 🎯 Objetivos principais:
- Identificação e validação da identidade do varejista
- Recolhimento e análise de dados/documentos obrigatórios
- Avaliação da reputação e relevância do vendedor
- Organização das informações operacionais e de negócio
- Preparação dos dados para uso nas demais áreas do marketplace

## 👥 Participantes do Time:

- João Pedro
- Marcella Palazzo
- Murilo Alves
- Victor Hugo Buiatti

## ✨ Configuração do ambiente local

### Linux 🐧

Todos os comandos serão via terminal.

Este _seed_ trabalha com o [Python 3.12](https://docs.python.org/3.12/), confirme se o mesmo está instalado em sua máquina.

Depois de clonar o projeto, acesse o diretório:

```sh
cd pc-identidade
```

Crie o [ambiente virtual](https://docs.python.org/3.12/tutorial/venv.html)
para instalar as bibliotecas e trabalharmos com o projeto:

```sh
make build-venv
# ou
# python3.12 -m venv venv
```

Uma vez criado o ambiente virtual do Python, você precisa ativá-lo
(estou supondo que você está no Linux 🐧):

```sh
. ./venv/bin/activate
```

Quaisquer comandos daqui para frente, iremos considerar que você está dentro
do ambiente virtual `(venv)`.

Instale as bibliotecas necessárias

```sh
pip install -r requirements.txt
```

Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:

```env
# Variáveis de Ambiente
ENV=dev

# MongoDB
APP_DB_URL_MONGO=mongodb://admin:admin@pc-identidade-mongo:27017/bd01?authSource=admin
MONGO_DB=pc_identidade

# Keycloak
KEYCLOAK_URL=http://pc-identidade-keycloak:8080
KEYCLOAK_REALM_NAME=marketplace
KEYCLOAK_CLIENT_ID=varejo
KEYCLOAK_WELL_KNOWN_URL=http://pc-identidade-keycloak:8080/realms/marketplace/.well-known/openid-configuration

# Credenciais Admin do Keycloak (usadas para criar usuários)
KEYCLOAK_ADMIN_USER=admin_marketplace
KEYCLOAK_ADMIN_PASSWORD=senha123
KEYCLOAK_ADMIN_CLIENT_ID=admin-cli
```

### Windows 🖥️

#### 1. Clone o repositório

```powershell
git clone https://github.com/projeto-carreira-luizalabs-2025/pc-identidade.git
cd pc-catalogo
```

#### 2. Crie o ambiente virtual

```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### 3. Instale as dependências

```powershell
pip install -r requirements.txt
```

#### 4. Configure variáveis de ambiente

Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:

```env
# Variáveis de Ambiente
ENV=dev

# MongoDB
APP_DB_URL_MONGO=mongodb://admin:admin@pc-identidade-mongo:27017/bd01?authSource=admin
MONGO_DB=pc_identidade

# Keycloak
KEYCLOAK_URL=http://pc-identidade-keycloak:8080
KEYCLOAK_REALM_NAME=marketplace
KEYCLOAK_CLIENT_ID=varejo
KEYCLOAK_WELL_KNOWN_URL=http://pc-identidade-keycloak:8080/realms/marketplace/.well-known/openid-configuration

# Credenciais Admin do Keycloak (usadas para criar usuários)
KEYCLOAK_ADMIN_USER=admin_marketplace
KEYCLOAK_ADMIN_PASSWORD=senha123
KEYCLOAK_ADMIN_CLIENT_ID=admin-cli
```

## 🐳 Instalação do Docker 

Para instalação do [Docker](https://docs.docker.com/engine/install/ubuntu/), siga o manual disponível no site oficial.

## ▶️ Executando o Projeto com Docker (Método Recomendado)

### Linux 🐧

Para construir a imagem Docker da aplicação, execute:

``` bash
make docker-build # Criará uma imagem com o nome pc/identidade.
```

Para rodar a aplicação em um contêiner Docker:

``` bash
make docker-run # Iniciará um contêiner chamado pc-identidade, expondo a porta 8000 do contêiner para a porta 8000 do seu host.
```

Se precisar acessar o shell do contêiner para depuração ou outras operações:

```bash
make docker-shell # Isso abrirá uma sessão bash interativa dentro do contêiner.
```

Use o comando para subir a api:

```bash
make run-dev
```

Acesse a doc da API em: [localhost:8000/api/docs](http://0.0.0.0:8000/api/docs) ou em [localhost:8000/redoc](http://0.0.0.0:8000/redoc)

### Windows 🖥️

#### 📦 Estrutura

- **MongoDB** e **KeyCloak** rodam via `docker-compose.yml`

#### 🚀 Passo a passo

1. Clonar o Repositório

Abra seu terminal e clone o projeto:

```sh
git clone [https://github.com/projeto-carreira-luizalabs-2025/pc-identidade.git](https://github.com/projeto-carreira-luizalabs-2025/pc-identidade.git)
cd pc-identidade
```

2. Configurar Variáveis de Ambiente

Crie um arquivo chamado .env na raiz do projeto. 

Este arquivo é crucial para a comunicação entre os contêineres. Copie e cole o seguinte conteúdo nele:

```env
# Variáveis de Ambiente
ENV=dev

# MongoDB
APP_DB_URL_MONGO=mongodb://admin:admin@pc-identidade-mongo:27017/bd01?authSource=admin
MONGO_DB=pc_identidade

# Keycloak
KEYCLOAK_URL=http://pc-identidade-keycloak:8080
KEYCLOAK_REALM_NAME=marketplace
KEYCLOAK_CLIENT_ID=varejo
KEYCLOAK_WELL_KNOWN_URL=http://pc-identidade-keycloak:8080/realms/marketplace/.well-known/openid-configuration

# Credenciais Admin do Keycloak (usadas para criar usuários)
KEYCLOAK_ADMIN_USER=admin_marketplace
KEYCLOAK_ADMIN_PASSWORD=senha123
KEYCLOAK_ADMIN_CLIENT_ID=admin-cli
```

3. Crie o ambiente virtual

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Instale as dependências

```powershell
pip install -r requirements.txt
```

4. Subir os Contêineres

Com o Docker em execução, use o seguinte comando para construir a imagem da sua aplicação e iniciar todos os serviços em segundo plano:

```bash
docker-compose up --build -d
```

Aguarde de 1 a 2 minutos para que todos os serviços, especialmente o Keycloak, iniciem completamente.

5. Configurando o Keycloak

Rode o seguinte comando para finalizar a configuração do Keycloak.

```bash
python ./devtools/keycloak-config/setup_sellers_attribute.py
```

6. Executando a Aplicação

Com todos os passos anteriores executados com sucesso, rode a aplicação localmente com o seguinte comando.

```bash
uvicorn app.api_main:app --reload --port 8000        
```

#### Comandos Úteis do Dia a Dia

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

#### Acessando os Serviços

- API da Aplicação (Swagger): http://localhost:8000/api/docs
- Admin Console do Keycloak: http://localhost:8080
  - **Usuário**: admin
  - **Senha**: admin

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
