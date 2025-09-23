# 🚀 Comandos de Instalação - SYNAPSE SIEM

## 📋 Debian/Ubuntu - Instalação Manual

### 1. Atualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar Python 3.11
```bash
sudo apt install python3.11 python3.11-venv python3.11-dev -y
```

### 3. Instalar Node.js 20
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
```

### 4. Instalar PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib -y
```

### 5. Instalar Dependências Adicionais
```bash
sudo apt install build-essential libpq-dev -y
```

### 6. Configurar PostgreSQL
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE siemdb;
CREATE USER siemuser WITH PASSWORD 'siempass';
GRANT ALL PRIVILEGES ON DATABASE siemdb TO siemuser;
\q
```

### 7. Configurar Backend
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgres://siemuser:siempass@localhost:5432/siemdb"
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 8. Configurar Frontend (Terminal Separado)
```bash
cd synapse_siem/frontend-mini
npm install
npm run dev
```

---

## 🪟 Windows - Instalação Manual

### 1. Configurar Backend
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install psycopg2-binary
$env:DATABASE_URL="postgres://siemuser:siempass@localhost:5432/siemdb"
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 2. Configurar Frontend (Terminal Separado)
```powershell
cd synapse_siem\frontend-mini
npm install
npm run dev
```

---

## 🐳 Docker - Debian/Ubuntu

### 1. Instalar Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install docker-compose-plugin -y
```

### 2. Executar Projeto
```bash
git clone <url-do-repositorio>
cd SYNAPSE
chmod +x docker-run.sh
./docker-run.sh
```

---

## 🐳 Docker - Windows

### 1. Executar Projeto
```powershell
git clone <url-do-repositorio>
cd SYNAPSE
docker compose up --build
```

---

## 🔧 Comandos Úteis

### Docker
```bash
# Parar serviços
docker compose down

# Ver logs
docker compose logs -f

# Executar comandos no container
docker compose exec backend python manage.py shell
docker compose exec backend python manage.py createsuperuser
```

### Desenvolvimento
```bash
# Ativar ambiente virtual (Linux)
source venv/bin/activate

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Instalar nova dependência
pip install nova-dependencia
pip freeze > requirements.txt

# Executar testes
python manage.py test

# Coletar arquivos estáticos
python manage.py collectstatic
```

### Frontend
```bash
# Limpar cache e reinstalar
rm -rf node_modules package-lock.json
npm install

# Build para produção
npm run build
```

---

## 🌐 Acessos Após Instalação

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **Banco de dados**: localhost:5432

---

## 🐛 Solução de Problemas

### Erro de Permissão Docker (Linux)
```bash
sudo usermod -aG docker $USER
# Fazer logout e login novamente
```

### Erro de Dependências Python
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Erro de Dependências Node
```bash
rm -rf node_modules package-lock.json
npm install
```

### Recriar Banco de Dados
```bash
# PostgreSQL
sudo -u postgres psql
DROP DATABASE siemdb;
CREATE DATABASE siemdb;
\q

# Django
python manage.py makemigrations
python manage.py migrate
```

---

## 📝 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgres://siemuser:siempass@localhost:5432/siemdb
SECRET_KEY=sua-chave-secreta-django
DEBUG=True
```

---

## ✅ API Key do Gemini

A API key do Gemini já está configurada no código, não é necessário configurar manualmente.
