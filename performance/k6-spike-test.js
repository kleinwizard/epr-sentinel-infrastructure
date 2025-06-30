import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '30s', target: 50 }, // Normal load
    { duration: '10s', target: 2000 }, // Sudden spike
    { duration: '30s', target: 2000 }, // Stay at spike
    { duration: '10s', target: 50 }, // Drop back to normal
    { duration: '30s', target: 50 }, // Normal load
    { duration: '10s', target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // Allow higher response times during spike
    http_req_failed: ['rate<0.3'], // Allow higher error rate during spike
  },
};

const BASE_URL = 'http://localhost:8001';

export default function() {
  const response = http.get(`${BASE_URL}/healthz`);
  
  check(response, {
    'healthcheck responds': (r) => r.status !== 0,
    'not server error': (r) => r.status < 500,
  }) || errorRate.add(1);

  sleep(0.1); // Very short sleep for spike test
}
