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

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
