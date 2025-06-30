import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '1m', target: 100 }, // Ramp up to 100 users
    { duration: '3m', target: 500 }, // Spike to 500 users
    { duration: '2m', target: 1000 }, // Spike to 1000 users
    { duration: '2m', target: 100 }, // Drop back to 100 users
    { duration: '1m', target: 0 }, // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests must complete below 1s
    http_req_failed: ['rate<0.2'], // Error rate must be below 20%
    errors: ['rate<0.2'],
  },
};

const BASE_URL = 'http://localhost:8001';

export default function() {
  const endpoints = [
    '/healthz',
    '/products/',
    '/materials/',
    '/fees/calculate?products=1,2,3'
  ];

  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const response = http.get(`${BASE_URL}${endpoint}`);
  
  check(response, {
    'status is not 500': (r) => r.status !== 500,
    'response time < 2s': (r) => r.timings.duration < 2000,
  }) || errorRate.add(1);

  sleep(0.5); // Shorter sleep for stress test
}
