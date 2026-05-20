from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.database import engine, Base
from app.routers import clients, beauty_services, appointments, reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria as tabelas do banco de dados na hora que liga a aplicação
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Cabeleleia Leila - Salão de Beleza",
    description=(
        "API para o sistema de agendamentos online da Cabeleleia Leila. "
        "Permite o gerenciamento de clientes, serviços de beleza, agendamentos, "
        "alterações com limite de antecedência, sugestões de datas e relatórios gerenciais semanais."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# adiciona as rotas de cada parte do sistema (clientes, serviços, agendamentos, relatórios)
app.include_router(clients.router)
app.include_router(beauty_services.router)
app.include_router(appointments.router)
app.include_router(reports.router)

import os
from fastapi.responses import HTMLResponse

@app.get("/", include_in_schema=False)
async def read_frontend():
    # Carrega e exibe a página HTML simples do frontend
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if not os.path.exists(template_path):
        return HTMLResponse(content="<h1>Erro: index.html não foi encontrado!</h1>", status_code=404)
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
