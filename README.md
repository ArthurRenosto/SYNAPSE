# SYNAPSE SIEM - Documentação Técnica

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios
```
SYNAPSE/
├── synapse_siem/                 # Módulo principal
│   ├── api/                      # Configuração Django
│   │   ├── settings.py          # Configurações do projeto
│   │   ├── urls.py              # URLs principais
│   │   └── wsgi.py              # WSGI para produção
│   ├── app/                     # Aplicações Django
│   │   └── logs/                # App de análise de logs
│   │       ├── models.py        # Modelos do banco
│   │       ├── views.py         # Views da API
│   │       ├── serializers.py   # Serializers DRF
│   │       └── urls.py          # URLs do app
│   ├── backend/                 # Engine de análise
│   │   ├── analyzer.py          # Analisador principal
│   │   ├── parsers.py           # Parsers de logs
│   │   ├── rules.py             # Sistema de regras
│   │   ├── rules.json           # Regras de detecção
│   │   ├── report.py            # Gerador de relatórios
│   │   └── utils.py             # Utilitários
│   ├── frontend/                # Interface React
│   │   ├── src/                 # Código fonte React
│   │   └── public/              # Arquivos estáticos
│   └── docker/                  # Configurações Docker
├── logs/                        # Logs para análise
└── requirements.txt             # Dependências Python
```

## 🔌 APIs Disponíveis

### Base URL: `http://localhost:8000`

#### 1. **Análise de Logs**
- **Endpoint**: `GET /api/logs/`
- **Descrição**: Analisa todos os logs da pasta `logs/` e retorna achados
- **Resposta**:
```json
{
  "analysis_id": 1,
  "total_logs": 4,
  "total_findings": 15,
  "by_severity": {
    "high": 5,
    "medium": 8,
    "low": 2
  },
  "findings": [
    {
      "file": "/path/to/log.txt",
      "line_number": 42,
      "content": "Failed login attempt from 192.168.1.100",
      "rule_name": "failed_login",
      "severity": "medium",
      "description": "Tentativa de login falhada detectada",
      "recommendation": "Verificar origem do IP"
    }
  ]
}
```

#### 2. **Histórico de Análises**
- **Endpoint**: `GET /api/logs/history/`
- **Descrição**: Lista as últimas 10 análises realizadas
- **Resposta**:
```json
[
  {
    "id": 1,
    "started_at": "2025-09-09T13:00:00Z",
    "completed_at": "2025-09-09T13:01:30Z",
    "total_files": 4,
    "total_findings": 15,
    "status": "completed"
  }
]
```

#### 3. **Admin Django**
- **Endpoint**: `GET /admin/`
- **Descrição**: Interface administrativa do Django

## 🗄️ Banco de Dados

### Modelos e Tabelas

#### 1. **LogFile** (`log_files`)
Armazena informações dos arquivos de log analisados:
```sql
CREATE TABLE log_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    analyzed_at TIMESTAMP DEFAULT NOW(),
    total_lines INTEGER DEFAULT 0
);
```

#### 2. **LogAnalysis** (`log_analyses`)
Registra cada execução de análise:
```sql
CREATE TABLE log_analyses (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP NULL,
    total_files INTEGER DEFAULT 0,
    total_findings INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'running'
);
```

#### 3. **LogFinding** (`log_findings`)
Armazena cada achado/alerta encontrado:
```sql
CREATE TABLE log_findings (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES log_analyses(id),
    log_file_id INTEGER REFERENCES log_files(id),
    line_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    rule_name VARCHAR(100) NOT NULL,
    severity VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT,
    timestamp TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_findings_severity ON log_findings(severity);
CREATE INDEX idx_findings_rule ON log_findings(rule_name);
CREATE INDEX idx_findings_created ON log_findings(created_at);
```

#### 4. **Rule** (`rules`)
Define regras de detecção personalizadas:
```sql
CREATE TABLE rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    pattern TEXT NOT NULL,
    severity VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    recommendation TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Engine de Análise

### Componentes Principais

#### 1. **LogAnalyzer** (`backend/analyzer.py`)
- Classe principal que coordena a análise
- Carrega regras do arquivo `rules.json`
- Processa arquivos de log linha por linha
- Aplica regras de detecção usando regex

#### 2. **Parsers** (`backend/parsers.py`)
- Detecta automaticamente formato dos logs
- Suporta: JSON, CSV, texto simples
- Extrai timestamps e estrutura dados

#### 3. **Rules Engine** (`backend/rules.py`)
- Carrega regras de `rules.json`
- Aplica padrões regex nos logs
- Classifica severidade dos achados

#### 4. **Report Generator** (`backend/report.py`)
- Gera relatórios em múltiplos formatos
- Suporta: JSON, CSV, Markdown, TXT
- Cria estatísticas e resumos

## 🐳 Docker e Deploy

### Serviços Docker

#### 1. **Backend (Django)**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### 2. **Frontend (React)**
```dockerfile
FROM node:20
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

#### 3. **Database (PostgreSQL)**
- Imagem: `postgres:15`
- Porta: `5432`
- Dados persistentes em volume Docker

### Configuração de Ambiente

#### Desenvolvimento Local
- **Backend**: SQLite (`db.sqlite3`)
- **Comando**: `python manage.py runserver`

#### Docker/Produção
- **Backend**: PostgreSQL
- **Variável**: `DATABASE_URL=postgres://user:pass@db:5432/dbname`

## 🚀 Como Executar

### 1. **Docker (Recomendado)**
```bash
# Build e start
cd synapse_siem
docker compose up --build

# Migrações
docker compose exec backend python manage.py migrate

# Criar superuser
docker compose exec backend python manage.py createsuperuser
```

### 2. **Desenvolvimento Local**
```bash
# Backend
cd synapse_siem
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (outro terminal)
cd synapse_siem/frontend
npm install
npm start
```

## 🔍 Fluxo de Análise

1. **Requisição**: Frontend chama `GET /api/logs/`
2. **Inicialização**: Cria registro `LogAnalysis` no banco
3. **Descoberta**: Encontra arquivos na pasta `logs/`
4. **Registro**: Salva arquivos na tabela `LogFile`
5. **Análise**: Engine processa logs com regras
6. **Persistência**: Salva achados na tabela `LogFinding`
7. **Resposta**: Retorna JSON com resultados
8. **Frontend**: Exibe resultados na interface

## 📊 Monitoramento

### Logs da Aplicação
- **Django**: Console e arquivo de log
- **Docker**: `docker compose logs -f`

### Métricas Disponíveis
- Total de análises realizadas
- Achados por severidade
- Performance por arquivo
- Histórico temporal

## 🔒 Segurança

### Configurações
- **DEBUG**: `False` em produção
- **SECRET_KEY**: Variável de ambiente
- **ALLOWED_HOSTS**: Configurar domínios
- **CORS**: Configurar origens permitidas

### Banco de Dados
- **Conexão**: SSL em produção
- **Credenciais**: Variáveis de ambiente
- **Backup**: Volumes persistentes
