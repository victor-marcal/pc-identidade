# PRimeira etapa: instalar os pacotes do Python
# Monstar a estrutura de arquivos da aplicac'ão
FROM python:3.12-slim AS constructor

SHELL ["/bin/bash", "-c"]

WORKDIR /pc-identidade

# Copia arquivo de dependências
COPY ./requirements/develop.txt .

# Copia pasta de dependências que possui base.txt
COPY requirements/ requirements/

# Instalar meus pacotes
RUN python -m venv venv && \
  .  venv/bin/activate && \
  pip install --upgrade pip && \
  pip install --no-cache-dir -r ./requirements/develop.txt

# Imagem final a ser entregue / conterá a minha aplicação
FROM python:3.12-slim 
ENV PATH=/pc-identidade/venv/bin:$PATH

# Setando variável ambiente como "dev"
ENV ENV=dev

WORKDIR /pc-identidade
COPY --from=constructor /pc-identidade/venv /pc-identidade/venv

# Verifica se o ambiente virtual foi criado corretamente
RUN /pc-identidade/venv/bin/python --version

COPY app /pc-identidade/app
COPY ./requirements/develop.txt /pc-identidade

RUN python -m compileall app

# Executável padrão
CMD [ "uvicorn", "app.api_main:app", "--host", "0.0.0.0", "--port", "8000" ]

# Montagem
# docker build -f ./devtools/docker/Dockerfile -t pc/preco .
# Execução
# docker run --rm -p 8000:8000 pc/preco