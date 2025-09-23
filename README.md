# SYNAPSE SIEM

Sistema de Gerenciamento de Eventos de Segurança da Informação (SIEM) com análise de logs usando IA.

## 🚀 Instalação e Execução

### ⚡ Instalação Automática

#### Para Debian/Ubuntu:
```bash
chmod +x install.sh
./install.sh
```

#### Para Windows:
```cmd
install.bat
```

### 🐳 Executar com Docker (Recomendado)

#### Debian/Ubuntu:
```bash
./docker-run.sh
```

#### Windows:
```cmd
docker compose up --build
```

### 🔧 Executar Manualmente

#### Debian/Ubuntu:
```bash
# Terminal 1 - Backend
source venv/bin/activate
python manage.py runserver

# Terminal 2 - Frontend
cd synapse_siem/frontend-mini
npm run dev
```

#### Windows:
```cmd
# Terminal 1 - Backend
venv\Scripts\activate
python manage.py runserver

# Terminal 2 - Frontend
cd synapse_siem\frontend-mini
npm run dev
```

## 🌐 Acessos

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin

## 📊 Funcionalidades

- **Análise de Logs**: Processamento e análise de logs de segurança
- **Dashboard**: Interface visual para monitoramento
- **IA Integration**: Análise inteligente usando Google Gemini
- **API REST**: Endpoints para integração com outros sistemas
- **Relatórios**: Geração automática de relatórios de segurança

## 🛠️ Comandos Úteis

### Docker:
```bash
# Parar serviços
docker compose down

# Ver logs
docker compose logs -f

# Executar comandos no container
docker compose exec backend python manage.py shell
docker compose exec backend python manage.py createsuperuser
```

### Desenvolvimento:
```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar nova dependência
pip install nova-dependencia
pip freeze > requirements.txt

# Executar testes
python manage.py test

# Coletar arquivos estáticos
python manage.py collectstatic
```

## 🐛 Solução de Problemas

### Problemas Comuns:

1. **Erro de conexão com banco:**
   - Verificar se PostgreSQL está rodando
   - Verificar credenciais no arquivo `.env`

2. **Erro de permissão Docker:**
   ```bash
   sudo usermod -aG docker $USER
   # Fazer logout e login novamente
   ```

3. **Erro de dependências Python:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

4. **Erro de dependências Node:**
   ```bash
   rm -rf node_modules package-lock.json
npm install
   ```

## 📝 Estrutura do Projeto

```
SYNAPSE/
├── synapse_siem/
│   ├── api/                 # Configurações Django
│   ├── app/logs/           # App de logs
│   ├── backend/            # Lógica de análise
│   ├── frontend-mini/      # Interface React
│   └── docker/             # Dockerfiles
├── logs/                   # Logs de exemplo
├── docker-compose.yml      # Configuração Docker
├── requirements.txt        # Dependências Python
└── README.md              # Este arquivo
```