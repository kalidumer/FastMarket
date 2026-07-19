// Base API Gateway configuration route
export const API_GATEWAY_URL = 'http://localhost:8000/api/v1';

// Direct Microservice endpoints (if not routing through a gateway)
export const AUTH_SERVICE_URL = 'http://localhost:8001';
export const PRODUCT_SERVICE_URL = 'http://localhost:8002';
export const ORDER_SERVICE_URL = 'http://localhost:8003';

// Client routing pathways
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  CART: '/cart',
  CHECKOUT: '/checkout',
  PAYMENT_SUCCESS: '/payment/success',
} as const;