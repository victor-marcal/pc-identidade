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
ENV=dev
APP_DB_URL_MONGO=mongodb://admin:admin@pc-identidade-mongo:27017/bd01?authSource=admin

MONGO_DB=pc_identidade
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
ENV=dev
APP_DB_URL_MONGO=mongodb://admin:admin@pc-identidade-mongo:27017/bd01?authSource=admin

MONGO_DB=pc_identidade
```

## 🐳 Instalação do Docker 

Para instalação do [Docker](https://docs.docker.com/engine/install/ubuntu/), siga o manual disponível no site oficial.

## ▶️ Execução usando Docker 

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
- **Aplicação FastAPI** roda com `Dockerfile` próprio
- **Ambos são containers separados**, que precisam se comunicar via **rede Docker**

#### 🚀 Passo a passo

1. Criar uma rede Docker compartilhada

Essa rede permitirá que os containers se comuniquem:

```bash
docker network create pc-net
```
Você só precisa fazer isso uma vez.

2. Subir o MongoDB e KeyCloak

```bash
docker compose -f docker-compose.yml up -d
```
Depois, conecte o container do Mongo e KeyCloak à rede:
```bash
docker network connect pc-net pc-identidade-mongo
docker network connect pc-net pc-identidade-keycloak-1
docker network connect pc-net pc-identidade-keycloak-db-1
```

3. Build da aplicação FastAPI

```bash
docker build -f ./devtools/docker/Dockerfile -t pc/identidade .
```

4. Rodar a aplicação (com .env e rede)

```bash
docker run --rm -p 8000:8000 --name pc-identidade-app ^
  --env-file .env ^
  --network pc-net ^
  pc/identidade
```

Use ^ no PowerShell. No bash, use ` ou escreva tudo em uma linha.

5. Testar se o Mongo está acessível

Em outro terminal, rode:

```bash
docker run --rm -it --network pc-net mongo mongosh "mongodb://admin:admin@pc-identidade-mongo:27017/bd01?authSource=admin"
```

Você verá o prompt bd01> se tudo estiver OK.


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

## 🔍 Análise com SonarQube

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

## 🗄️ Subindo e Parando o MongoDB com Docker Compose

Para iniciar o banco de dados MongoDB utilizando Docker Compose, execute:

```bash
make docker-compose-mongo-up
```

Isso irá subir o serviço MongoDB definido em `devtools/docker/docker-compose-mongo.yml`.

Para parar e remover o serviço do MongoDB, execute:

```bash
make docker-compose-mongo-down
```

Esses comandos garantem que o banco de dados MongoDB estará disponível para a aplicação durante o desenvolvimento e podem ser usados sempre que precisar iniciar ou parar o banco.

## Contribuições e Atualizações
O projeto está aberto a contribuições e atualizações da comunidade. O processo para contribuições é o seguinte:

* **Pull Requests**: Contribuições devem ser submetidas como pull requests.
* **Code Review**: Cada pull request passará por um code review detalhado pela equipe. Isso garante que o código esteja alinhado com os padrões de qualidade e funcionamento do projeto.
* **Incorporação de Mudanças**: Após a aprovação no code review, as mudanças serão integradas ao código principal.

## 📖 Recursos úteis

- [Conventional Commits](https://www.conventionalcommits.org)