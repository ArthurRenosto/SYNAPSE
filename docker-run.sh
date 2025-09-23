#!/bin/bash

echo "🐳 SYNAPSE Docker Setup"
echo "======================"

# Build e start dos containers
echo "📦 Building containers..."
docker compose build

echo "🚀 Starting services..."
docker compose up   

sleep 10

echo "⏳ Waiting for database..."
sleep 5

echo "🔧 Creating migrations..."
docker compose exec backend python manage.py makemigrations

echo "🔧 Running migrations..."
docker compose exec backend python manage.py migrate

echo "✅ Setup complete!"
echo ""
echo "🌐 Services running:"
echo "   - Backend API: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo "   - Database: localhost:5432"
echo ""
echo "📊 Test the API:"
echo "   curl http://localhost:8000/api/logs/"
echo ""
echo "👤 Create admin user:"
echo "   docker compose exec backend python manage.py createsuperuser"
echo ""
echo "🛑 To stop: docker compose down"
