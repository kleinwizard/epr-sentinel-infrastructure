import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 50 }, // Ramp up to 50 users
    { duration: '5m', target: 200 }, // Stay at 200 users for 5 minutes
    { duration: '2m', target: 0 }, // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<250'], // 95% of requests must complete below 250ms
    http_req_failed: ['rate<0.1'], // Error rate must be below 10%
    errors: ['rate<0.1'], // Custom error rate must be below 10%
  },
};

const BASE_URL = 'http://localhost:8001';

const testUser = {
  email: 'loadtest@example.com',
  password: 'loadtestpassword123'
};

let authToken = '';

export function setup() {
  const loginResponse = http.post(`${BASE_URL}/auth/login`, {
    username: testUser.email,
    password: testUser.password
  });
  
  if (loginResponse.status === 200) {
    const responseBody = JSON.parse(loginResponse.body);
    return { token: responseBody.access_token };
  }
  
  return { token: '' };
}

export default function(data) {
  const headers = data.token ? {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json'
  } : {
    'Content-Type': 'application/json'
  };

  const scenarios = [
    { name: 'healthcheck', weight: 10, func: testHealthCheck },
    { name: 'products', weight: 30, func: testProducts },
    { name: 'materials', weight: 20, func: testMaterials },
    { name: 'fees', weight: 25, func: testFees },
    { name: 'reports', weight: 15, func: testReports }
  ];

  const totalWeight = scenarios.reduce((sum, s) => sum + s.weight, 0);
  const random = Math.random() * totalWeight;
  let currentWeight = 0;
  
  for (const scenario of scenarios) {
    currentWeight += scenario.weight;
    if (random <= currentWeight) {
      scenario.func(headers);
      break;
    }
  }

  sleep(1);
}

function testHealthCheck(headers) {
  const response = http.get(`${BASE_URL}/healthz`);
  
  check(response, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 100ms': (r) => r.timings.duration < 100,
  }) || errorRate.add(1);
}

function testProducts(headers) {
  const listResponse = http.get(`${BASE_URL}/products/`, { headers });
  
  check(listResponse, {
    'products list status is 200': (r) => r.status === 200,
    'products list response time < 250ms': (r) => r.timings.duration < 250,
  }) || errorRate.add(1);

  if (listResponse.status === 200) {
    const newProduct = {
      name: `Load Test Product ${Math.random()}`,
      description: 'Product created during load testing',
      category: 'Electronics',
      weight: Math.random() * 10,
      material_composition: {
        plastic: 70,
        metal: 30
      }
    };

    const createResponse = http.post(`${BASE_URL}/products/`, JSON.stringify(newProduct), { headers });
    
    check(createResponse, {
      'product creation status is 201': (r) => r.status === 201,
      'product creation response time < 500ms': (r) => r.timings.duration < 500,
    }) || errorRate.add(1);
  }
}

function testMaterials(headers) {
  const response = http.get(`${BASE_URL}/materials/`, { headers });
  
  check(response, {
    'materials list status is 200': (r) => r.status === 200,
    'materials list response time < 200ms': (r) => r.timings.duration < 200,
  }) || errorRate.add(1);
}

function testFees(headers) {
  const feeParams = {
    products: [1, 2, 3], // Assuming these product IDs exist
    period: 'Q1-2024'
  };

  const response = http.get(`${BASE_URL}/fees/calculate?${new URLSearchParams(feeParams)}`, { headers });
  
  check(response, {
    'fee calculation status is 200': (r) => r.status === 200,
    'fee calculation response time < 300ms': (r) => r.timings.duration < 300,
  }) || errorRate.add(1);
}

function testReports(headers) {
  const listResponse = http.get(`${BASE_URL}/reports/`, { headers });
  
  check(listResponse, {
    'reports list status is 200': (r) => r.status === 200,
    'reports list response time < 250ms': (r) => r.timings.duration < 250,
  }) || errorRate.add(1);

  if (listResponse.status === 200) {
    const reportData = {
      title: `Load Test Report ${Date.now()}`,
      type: 'monthly',
      start_date: '2024-01-01',
      end_date: '2024-01-31'
    };

    const generateResponse = http.post(`${BASE_URL}/reports/generate`, JSON.stringify(reportData), { headers });
    
    check(generateResponse, {
      'report generation status is 201': (r) => r.status === 201,
      'report generation response time < 1000ms': (r) => r.timings.duration < 1000,
    }) || errorRate.add(1);
  }
}

export function teardown(data) {
  console.log('Load test completed');
}
