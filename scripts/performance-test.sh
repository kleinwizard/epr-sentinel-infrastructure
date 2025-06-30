#!/bin/bash

set -e

echo "🚀 Starting performance testing suite..."

mkdir -p performance-reports

if ! command -v k6 &> /dev/null; then
    echo "Installing k6..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo gpg -k
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install k6
    else
        echo "Please install k6 manually: https://k6.io/docs/getting-started/installation/"
        exit 1
    fi
fi

echo "🔧 Starting backend server..."
cd backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to start..."
sleep 10

if ! curl -f http://localhost:8001/healthz > /dev/null 2>&1; then
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend is running"

echo "📊 Running load test..."
k6 run --out json=performance-reports/load-test-results.json performance/k6-load-test.js

echo "💪 Running stress test..."
k6 run --out json=performance-reports/stress-test-results.json performance/k6-stress-test.js

echo "⚡ Running spike test..."
k6 run --out json=performance-reports/spike-test-results.json performance/k6-spike-test.js

echo "🛑 Stopping backend server..."
kill $BACKEND_PID 2>/dev/null || true

echo "🔍 Running Lighthouse performance audit..."

cd frontend
npm run build
npx serve -s dist -l 8080 &
FRONTEND_PID=$!
cd ..

echo "⏳ Waiting for frontend to start..."
sleep 5

if ! curl -f http://localhost:8080 > /dev/null 2>&1; then
    echo "❌ Frontend failed to start"
    kill $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Frontend is running"

cd frontend
npm run lighthouse
mv lighthouse-report.html ../performance-reports/
cd ..

echo "🛑 Stopping frontend server..."
kill $FRONTEND_PID 2>/dev/null || true

echo "✅ Performance testing complete!"
echo "📊 Reports saved in performance-reports/"
echo "- Load test: performance-reports/load-test-results.json"
echo "- Stress test: performance-reports/stress-test-results.json"
echo "- Spike test: performance-reports/spike-test-results.json"
echo "- Lighthouse: performance-reports/lighthouse-report.html"
