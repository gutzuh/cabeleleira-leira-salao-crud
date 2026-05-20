# Sistema de Agendamentos — Cabeleleia Leila

Este projeto consiste em um sistema completo para gerenciamento de clientes, serviços e agendamentos de um salão de beleza. A solução foi desenvolvida utilizando uma arquitetura modular em Python com FastAPI para o backend, integrada a um painel de controle administrativo em HTML5 e Bootstrap 5 servido diretamente pela própria aplicação.

O projeto foi construído focando em organização de código, manutenibilidade e separação de responsabilidades (camadas HTTP, serviços com regras de negócio e camada de persistência de dados).

---

## Estrutura do Projeto

O código do sistema está organizado da seguinte forma:

`tree -I "__pycache__|.venv|*.pyc|.git|.pdf"`

```text
Cabeleleia Leila/
├── app/
│   ├── database.py         # Configuração do SQLAlchemy e provimento de sessão local
│   ├── enums.py            # Definição de estados estáveis de agendamentos e serviços
│   ├── main.py             # Arquivo de inicialização do app e roteamento raiz
│   ├── models.py           # Modelagem de dados relacional com SQLAlchemy 2.0
│   ├── schemas.py          # Contratos de validação e serialização de dados (Pydantic v2)
│   ├── routers/
│   │   ├── appointments.py # Endpoints HTTP relativos ao fluxo de agendamentos
│   │   ├── beauty_services.py # Endpoints HTTP para cadastro do catálogo de serviços
│   │   ├── clients.py      # Endpoints HTTP para manutenção de clientes
│   │   └── reports.py      # Endpoint HTTP de agregação de relatórios semanais
│   └── services/
│       ├── appointment_service.py # Regras de domínio e lógica operacional de agendamentos
│       └── report_service.py      # Lógica de agregação SQL e faturamento semanal
├── requirements.txt        # Dependências de execução declaradas
└── README.md               # Documentação técnica do projeto
```

---

## Tecnologias Utilizadas

* **Python 3**: Linguagem base do projeto.
* **FastAPI**: Framework de alto desempenho utilizado para a construção e disponibilização das rotas RESTful.
* **SQLAlchemy 2.0**: ORM utilizado para abstração de banco de dados, utilizando mapeamento declarativo moderno e tipado
* **SQLite**: Banco de dados relacional leve e embutido para persistência local dos registros.
* **Pydantic v2**: Camada robusta de validação e parsing de schemas e dados de entrada/saída.
* **Bootstrap 5 & JavaScript (Puro) & FullCalendar 6**: Stack utilizada para o desenvolvimento da Single Page Application (SPA) que serve como painel administrativo do salão.

---

## Instruções de Como Rodar o Projeto

Para executar o projeto localmente, siga os passos descritos abaixo.

### 1. Criar e Ativar o Ambiente Virtual
Navegue até a pasta raiz do projeto no terminal e crie o ambiente isolado do Python:

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar as Dependências
Instale as dependências declaradas no arquivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Executar o Servidor de Desenvolvimento
Inicie o servidor local através do Uvicorn:
```bash
uvicorn app.main:app --reload
```

A aplicação estará disponível em:
* **Painel Administrativo (Interface)**: `http://127.0.0.1:8000`
* **Documentação interativa da API (Swagger)**: `http://127.0.0.1:8000/docs`

---

## Observações de Implementação e Regras de Negócio

### 1. Separação Estrita de Responsabilidades
A arquitetura foi estruturada para evitar o acoplamento de código:
* Os arquivos na pasta `routers/` são responsáveis exclusivamente por receber requisições HTTP, delegar a execução para a camada de serviços e formatar as respostas JSON através de schemas do Pydantic.
* Os arquivos na pasta `services/` centralizam a inteligência de negócios, validações relacionais e interações diretas com o banco de dados via sessão do SQLAlchemy.

### 2. Snapshots Históricos de Preço e Duração
Para garantir a integridade dos dados históricos do salão, o relacionamento associativo entre agendamentos e serviços armazena os valores de preço (`price_at_booking`) e duração (`duration_at_booking`) no momento exato em que a reserva é feita. Isso impede que reajustes futuros de preços no catálogo de serviços alterem retroativamente o faturamento de agendamentos passados.

### 3. Regra de Limite de Antecedência para Alterações
Visando evitar inconsistências de agenda de última hora, o sistema impede a modificação ou cancelamento de agendamentos caso o tempo restante para o início programado seja inferior a 48 horas (2 dias). Nesses casos, o backend retorna um erro com a mensagem orientando o cliente a entrar em contato diretamente por telefone.

### 4. Sugestão Inteligente de Reagendamento Semanal
Quando um cliente cria um agendamento, o sistema verifica automaticamente se ele já possui outro compromisso na mesma semana calendário (segunda-feira a domingo). Em caso positivo, um aviso amigável é retornado junto aos dados do agendamento sugerindo concentrar as visitas na mesma data para maior comodidade.

### 5. Relatórios Baseados em Semana Calendário
O relatório semanal para a administração é filtrado por uma data de referência que calcula a faixa da semana calendário abrangida (de segunda-feira às 00:00 a domingo às 23:59:59). O cálculo de faturamento exibido leva em consideração exclusivamente o valor dos serviços cujos status individuais estejam definidos como concluídos.
