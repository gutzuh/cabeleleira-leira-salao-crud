# Cabeleleia Leila — API de Agendamentos

API backend desenvolvida para gerenciamento de clientes, serviços e agendamentos do salão **Cabeleleia Leila**.

A aplicação foi construída utilizando **FastAPI**, com organização modular e separação clara de responsabilidades entre camada HTTP, regras de negócio e persistência de dados.

O projeto foi estruturado visando:

- facilidade de manutenção;
- legibilidade de código;
- isolamento de responsabilidades;
- previsibilidade de regras de negócio;
- evolução incremental da aplicação.

---

# Tecnologias Utilizadas

- Python 3
- FastAPI
- SQLAlchemy 2.0
- SQLite
- Pydantic v2
- Uvicorn

---

# Estrutura do Projeto

`tree -I '__pycache__|.venv|*.pyc|.git|*.pdf'`

```text
Cabeleleia Leila/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── enums.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── appointments.py
│   │   ├── beauty_services.py
│   │   ├── clients.py
│   │   └── reports.py
│   └── services/
│       ├── __init__.py
│       ├── appointment_service.py
│       └── report_service.py
├── requirements.txt
└── README.md
```

---

# Organização da Aplicação

## Camada de Rotas

Os arquivos dentro de `routers/` possuem responsabilidade exclusiva sobre o fluxo HTTP da aplicação.

Nessa camada ficam centralizados:

- endpoints;
- parâmetros de requisição;
- status HTTP;
- serialização de resposta;
- integração com FastAPI.

As rotas não concentram regras de negócio diretamente, mantendo a aplicação desacoplada e mais simples de manter.

---

## Camada de Serviços

A pasta `services/` centraliza toda a lógica operacional da aplicação.

As principais responsabilidades dessa camada incluem:

- criação e atualização de agendamentos;
- validações temporais;
- cálculo automático de duração dos serviços;
- manipulação de status;
- composição de respostas;
- geração de relatórios.

Essa separação evita duplicação de lógica entre endpoints e facilita futuras expansões da aplicação.

---

## Persistência e Modelagem

A modelagem foi construída utilizando SQLAlchemy 2.0 com relacionamentos explícitos entre entidades.

A estrutura contempla:

- clientes;
- serviços;
- agendamentos;
- relacionamento entre agendamento e serviços;
- armazenamento histórico de preço e duração no momento da reserva.

O relacionamento entre agendamentos e serviços foi modelado de forma associativa para permitir controle individual de status por serviço.

---

## Validação de Dados

Os contratos de entrada e saída da API utilizam Pydantic v2.

Os schemas foram separados dos models para evitar acoplamento entre estrutura de banco e payloads HTTP, mantendo a API mais previsível e controlada.

---

# Configuração do Ambiente

## Criar ambiente virtual

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

# Executando a Aplicação

```bash
uvicorn app.main:app --reload
```

A aplicação ficará disponível em:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

---

# Funcionalidades Implementadas

## Gestão de Clientes

A API permite cadastro e gerenciamento de clientes utilizados durante o fluxo de agendamento.

Os dados são persistidos de forma relacional e utilizados como referência em todas as operações do sistema.

---

## Gestão de Serviços

Os serviços do salão podem ser cadastrados contendo:

- nome;
- descrição;
- duração;
- preço.

As informações são utilizadas posteriormente durante a composição dos agendamentos e geração de relatórios.

---

## Gestão de Agendamentos

O fluxo principal da aplicação contempla:

- criação de agendamentos;
- associação de múltiplos serviços;
- cálculo automático de horário final;
- confirmação de atendimento;
- atualização de dados do agendamento;
- controle de status.

A duração total do atendimento é calculada dinamicamente com base na soma dos serviços associados.

---

## Controle Individual de Serviços

Cada serviço associado ao agendamento possui status independente.

Isso permite um controle operacional mais granular durante o atendimento, possibilitando rastrear exatamente quais serviços foram:

- concluídos;
- cancelados;
- iniciados;
- mantidos pendentes.

---

## Regras de Alteração de Agendamento

A aplicação possui validação de bloqueio para alterações próximas da data marcada.

Quando faltam menos de 48 horas para o atendimento, a atualização do agendamento é interrompida e a API retorna uma mensagem de regra de negócio apropriada.

Essa abordagem evita inconsistências operacionais e simula um fluxo mais próximo de uma operação real de salão.

---

## Snapshot Histórico de Serviços

No momento da criação do agendamento, o sistema armazena o valor e duração original dos serviços vinculados.

Isso garante consistência histórica mesmo em cenários onde o catálogo sofre alterações posteriores.

Sem esse controle, relatórios antigos poderiam sofrer inconsistência após reajustes de preço ou alteração de duração dos serviços.

---

## Relatórios Semanais

A API possui endpoint para geração de relatório semanal consolidado.

Os dados retornados incluem:

- total de agendamentos;
- serviços concluídos;
- faturamento estimado;
- agrupamento por status;
- serviços mais solicitados.

As consultas são processadas diretamente na camada de serviço utilizando agregações SQL para reduzir processamento desnecessário na aplicação.

---

# Estrutura de Endpoints

```text
POST   /clients
POST   /services

POST   /appointments
POST   /appointments/{id}/confirm

PUT    /appointments/{id}

PATCH  /appointments/{appointment_id}/services/{service_id}/status

GET    /reports/weekly
```
