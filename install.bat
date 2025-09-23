@echo off
echo 🚀 SYNAPSE SIEM - Instalação Automática para Windows
echo ====================================================

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python não encontrado! Instale Python 3.11+ primeiro.
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar se Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js não encontrado! Instale Node.js 20+ primeiro.
    echo Baixe em: https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker não encontrado!
    echo Para instalação completa, baixe Docker Desktop em: https://www.docker.com/products/docker-desktop/
    echo Continuando com instalação manual...
    echo.
)

echo [INFO] Python e Node.js encontrados!
echo.

REM Criar ambiente virtual
echo [INFO] Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Falha ao criar ambiente virtual!
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualizar pip
echo [INFO] Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependências Python
echo [INFO] Instalando dependências Python...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Falha ao instalar dependências Python!
    pause
    exit /b 1
)

REM Instalar psycopg2-binary para Windows
echo [INFO] Instalando psycopg2-binary...
pip install psycopg2-binary

REM Configurar variáveis de ambiente
echo [INFO] Configurando variáveis de ambiente...
set DATABASE_URL=postgres://siemuser:siempass@localhost:5432/siemdb

REM Executar migrações
echo [INFO] Executando migrações do Django...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo [WARNING] Falha ao criar migrações. Continuando...
)

python manage.py migrate
if %errorlevel% neq 0 (
    echo [WARNING] Falha ao executar migrações. Continuando...
)

REM Perguntar sobre superusuário
echo.
echo [WARNING] Deseja criar um superusuário? (y/n)
set /p create_superuser=
if /i "%create_superuser%"=="y" (
    echo [INFO] Criando superusuário...
    python manage.py createsuperuser
)

REM Configurar frontend
echo [INFO] Configurando frontend...
cd synapse_siem\frontend-mini
if %errorlevel% neq 0 (
    echo [ERROR] Diretório frontend não encontrado!
    pause
    exit /b 1
)

echo [INFO] Instalando dependências do frontend...
npm install
if %errorlevel% neq 0 (
    echo [ERROR] Falha ao instalar dependências do frontend!
    pause
    exit /b 1
)

cd ..\..

echo.
echo [SUCCESS] ✅ Instalação concluída!
echo.
echo 🚀 Para executar o projeto, escolha uma opção:
echo.
echo 📦 OPÇÃO 1 - Docker (Recomendado):
echo    docker compose up --build
echo.
echo 🔧 OPÇÃO 2 - Manual:
echo    Backend:  venv\Scripts\activate ^&^& python manage.py runserver
echo    Frontend: cd synapse_siem\frontend-mini ^&^& npm run dev
echo.
echo 📊 Acessos:
echo    - Frontend: http://localhost:3000
echo    - Backend:  http://localhost:8000
echo    - Admin:    http://localhost:8000/admin
echo.
echo [WARNING] Para Docker: execute docker compose up --build
echo [WARNING] Para Manual: execute os comandos em terminais separados!
echo.
pause
