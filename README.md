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
1. Clonar o repositório (ou baixar a pasta)
git clone https://github.com/JoaoSaint/Desafio-Bild
cd Desafio-Bild

2. Criar e ativar o ambiente virtual

python -m venv .venv
.\.venv\Scripts\Activate.ps1

3. Instalar dependências
pip install -r requirements.txt

4. Iniciar o servidor
uvicorn app.main:app --reload

O servidor ficará disponível em:

http://127.0.0.1:8000

## Testando a API
Depois de subir o servidor, acesse:

http://127.0.0.1:8000/docs

Lá é possível testar o POST /plan-activity diretamente pelo navegador.

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


## Próximos passos (em pausa)

### Criar uma interface web simples que consuma o POST /plan-activity.

Objetivo: enaltecer o backend e suas funcionalidades, oferecendo uma forma
rápida e intuitiva de testar o serviço de forma visual.