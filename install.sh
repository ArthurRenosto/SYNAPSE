#!/bin/bash

echo "🚀 SYNAPSE SIEM - Instalação Automática para Debian/Ubuntu"
echo "=========================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    print_error "Não execute este script como root!"
    print_warning "Execute como usuário normal. O script pedirá sudo quando necessário."
    exit 1
fi

# Atualizar sistema
print_status "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11
print_status "Instalando Python 3.11..."
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Instalar Node.js 20
print_status "Instalando Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

# Instalar PostgreSQL
print_status "Instalando PostgreSQL..."
sudo apt install postgresql postgresql-contrib -y

# Instalar dependências adicionais
print_status "Instalando dependências adicionais..."
sudo apt install build-essential libpq-dev -y

# Instalar Docker
print_status "Instalando Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install docker-compose-plugin -y
rm get-docker.sh

# Configurar PostgreSQL
print_status "Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE siemdb;" 2>/dev/null || print_warning "Banco siemdb já existe"
sudo -u postgres psql -c "CREATE USER siemuser WITH PASSWORD 'siempass';" 2>/dev/null || print_warning "Usuário siemuser já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE siemdb TO siemuser;" 2>/dev/null

# Configurar backend
print_status "Configurando backend..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variáveis de ambiente
export DATABASE_URL="postgres://siemuser:siempass@localhost:5432/siemdb"

# Executar migrações
print_status "Executando migrações do Django..."
python manage.py makemigrations
python manage.py migrate

# Criar superusuário (opcional)
print_warning "Deseja criar um superusuário? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

# Configurar frontend
print_status "Configurando frontend..."
cd synapse_siem/frontend-mini
npm install
cd ../..

print_success "✅ Instalação concluída!"
echo ""
echo "🚀 Para executar o projeto, escolha uma opção:"
echo ""
echo "📦 OPÇÃO 1 - Docker (Recomendado):"
echo "   ./docker-run.sh"
echo ""
echo "🔧 OPÇÃO 2 - Manual:"
echo "   Backend:  source venv/bin/activate && python manage.py runserver"
echo "   Frontend: cd synapse_siem/frontend-mini && npm run dev"
echo ""
echo "📊 Acessos:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend:  http://localhost:8000"
echo "   - Admin:    http://localhost:8000/admin"
echo ""
print_warning "Para Docker: execute ./docker-run.sh"
print_warning "Para Manual: execute os comandos em terminais separados!"
