import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('/auth/login', () => {
    return HttpResponse.json({
      access_token: 'mock-jwt-token',
      token_type: 'bearer',
      user: {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        is_active: true
      }
    })
  }),

  http.post('/auth/register', () => {
    return HttpResponse.json({
      id: 1,
      email: 'test@example.com',
      username: 'testuser',
      is_active: true
    }, { status: 201 })
  }),

  http.get('/auth/me', () => {
    return HttpResponse.json({
      id: 1,
      email: 'test@example.com',
      username: 'testuser',
      is_active: true
    })
  }),

  http.get('/products/', () => {
    return HttpResponse.json([
      {
        id: 1,
        name: 'Test Product',
        description: 'A test product',
        category: 'Electronics',
        weight: 1.5,
        material_composition: { plastic: 80, metal: 20 }
      }
    ])
  }),

  http.post('/products/', () => {
    return HttpResponse.json({
      id: 2,
      name: 'New Product',
      description: 'A new product',
      category: 'Electronics',
      weight: 2.0,
      material_composition: { plastic: 70, metal: 30 }
    }, { status: 201 })
  }),

  http.get('/materials/', () => {
    return HttpResponse.json([
      {
        id: 1,
        name: 'Plastic',
        category: 'Polymer',
        epr_rate: 0.15,
        unit: 'kg'
      },
      {
        id: 2,
        name: 'Aluminum',
        category: 'Metal',
        epr_rate: 0.25,
        unit: 'kg'
      }
    ])
  }),

  http.get('/fees/calculate', () => {
    return HttpResponse.json({
      total_fee: 125.50,
      breakdown: {
        plastic: 75.30,
        metal: 50.20
      },
      currency: 'USD'
    })
  }),

  http.get('/reports/', () => {
    return HttpResponse.json([
      {
        id: 1,
        title: 'Q1 2024 Compliance Report',
        status: 'completed',
        created_at: '2024-01-15T10:00:00Z',
        file_url: '/files/report-q1-2024.pdf'
      }
    ])
  }),

  http.post('/reports/generate', () => {
    return HttpResponse.json({
      id: 2,
      title: 'Q2 2024 Compliance Report',
      status: 'processing',
      created_at: '2024-04-15T10:00:00Z'
    }, { status: 201 })
  }),

  http.post('/files/upload', () => {
    return HttpResponse.json({
      id: 1,
      filename: 'test-upload.csv',
      size: 1024,
      url: '/files/test-upload.csv'
    }, { status: 201 })
  }),

  http.post('/payments/create-intent', () => {
    return HttpResponse.json({
      client_secret: 'pi_test_123_secret_test',
      payment_intent_id: 'pi_test_123'
    })
  }),

  http.get('/healthz', () => {
    return HttpResponse.json({
      status: 'ok',
      message: 'EPR Co-Pilot Backend is running'
    })
  }),

  http.all('*', ({ request }) => {
    console.warn(`Unhandled ${request.method} request to ${request.url}`)
    return new HttpResponse(null, { status: 404 })
  })
]
