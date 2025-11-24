# Serviço de Planejamento de Atividades ao Ar Livre

Este projeto implementa um **serviço backend** que recomenda atividades ao ar livre
com base nos horários de nascer e pôr do sol para uma determinada localização e data.

Ele expõe uma API HTTP com uma rota principal:

- `POST /plan-activity`

que consulta a API pública [Sunrise-Sunset](https://sunrise-sunset.org/api)
e devolve:

- horário de nascer do sol (`sunrise`)
- horário de pôr do sol (`sunset`)
- duração do dia (`day_length`)
- sugestões de atividades baseadas nesses horários (`activities`)

---

## Stack e requisitos

- Python 3.10+ (testado em Windows)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/) (servidor ASGI)
- [httpx](https://www.python-httpx.org/) (cliente HTTP assíncrono)

As dependências estão listadas em:

requirements.txt

## Como rodar o projeto

1. Clonar o repositório (ou baixar a pasta raiz).

git clone https://github.com/JoaoSaint/Desafio-Bild

cd Desafio-Bild

2. Criar e ativar o ambiente virtual

python -m venv .venv
.\.venv\Scripts\Activate.ps1

3. Instalar dependências
pip install -r requirements.txt

4. Iniciar o servidor
uvicorn app.main:app --reload

## Testando a API

Depois de subir o servidor, acesse:

http://127.0.0.1:8000/docs

Lá é possível usar o POST /plan-activity diretamente pelo navegador.

O Serviço também conta com um frontend simples(totalmente opcional) que consome os dados das rotas e da API, e pode ser acessado em http://127.0.0.1:8000/frontend/

Tem como intuito mostrar de forma mais intuitiva e simplificada as funcionalidades do serviço.

Dentro do mesmo pode-se utilizar de um "Modo Formulário" onde o usuário preenche os dados de Latitude, Longitude e Data e o próprio formulário gera um body JSON e envia à API.

Da mesma forma que se pode injetar o body JSON diretamente no "Modo JSON"(equivalente ao que se colocaria na /docs) e receber a mesma saída da API.
### Exemplo de requisição

POST /plan-activity

Body (JSON):

{
  "latitude": 36.72016,
  "longitude": -4.42034,
  "date": "2021-12-25"
}


Exemplo de resposta (pode variar conforme a API externa):

{
  "sunrise": "4:26:47 AM",
  "sunset": "2:08:55 PM",
  "day_length": "09:42:08",
  "activities": [
    "Caminhada ao nascer do sol às 4:26 AM",
    "Piquenique durante o dia",
    "Fotografia ao pôr do sol às 2:08 PM",
    "Observação de estrelas após o pôr do sol"
  ]
}