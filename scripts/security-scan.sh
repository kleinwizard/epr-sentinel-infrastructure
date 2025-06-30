#!/bin/bash

set -e

echo "🔒 Starting comprehensive security scan..."

mkdir -p security-reports

echo "📦 Scanning frontend dependencies..."
cd frontend

echo "Running npm audit..."
npm audit --audit-level=moderate --json > ../security-reports/npm-audit.json || true
npm audit --audit-level=moderate > ../security-reports/npm-audit.txt || true

cd ..

echo "🐍 Scanning backend dependencies..."
cd backend

echo "Running pip-audit..."
poetry export -f requirements.txt --output requirements.txt --without-hashes
pip-audit -r requirements.txt --format=json --output=../security-reports/pip-audit.json || true
pip-audit -r requirements.txt --output=../security-reports/pip-audit.txt || true
rm requirements.txt

echo "Running Bandit security scan..."
poetry run bandit -r . -f json -o ../security-reports/bandit.json || true
poetry run bandit -r . -o ../security-reports/bandit.txt || true

cd ..

echo "🔍 Running Trivy filesystem scan..."
if command -v trivy &> /dev/null; then
    trivy fs . --format json --output security-reports/trivy.json || true
    trivy fs . --output security-reports/trivy.txt || true
else
    echo "Trivy not installed, skipping filesystem scan"
fi

echo "🕵️ Running TruffleHog secrets scan..."
if command -v trufflehog &> /dev/null; then
    trufflehog git file://. --json > security-reports/trufflehog.json || true
    trufflehog git file://. > security-reports/trufflehog.txt || true
else
    echo "TruffleHog not installed, skipping secrets scan"
fi

echo "🐳 Running Docker security scan..."
if command -v docker &> /dev/null; then
    if command -v hadolint &> /dev/null; then
        hadolint backend/Dockerfile > security-reports/hadolint-backend.txt || true
        hadolint frontend/Dockerfile > security-reports/hadolint-frontend.txt || true
    else
        echo "Hadolint not installed, skipping Dockerfile scan"
    fi
else
    echo "Docker not available, skipping Docker security scan"
fi

echo "✅ Security scan complete! Reports saved in security-reports/"
echo "📊 Summary:"
echo "- NPM audit: security-reports/npm-audit.txt"
echo "- Pip audit: security-reports/pip-audit.txt"
echo "- Bandit: security-reports/bandit.txt"
echo "- Trivy: security-reports/trivy.txt"
echo "- TruffleHog: security-reports/trufflehog.txt"
