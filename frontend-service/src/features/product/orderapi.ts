import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../store';
import {
  CartItem,
  CheckoutRequest,
  CheckoutResponse,
  VerificationResponse,
  Product,
} from '../types/productType';

export const orderApi = createApi({
  reducerPath: 'orderApi',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8007/api/order',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Cart', 'Order', 'Recommendations'],
  endpoints: (builder) => ({
    // Add / Update Cart Item
    addToCart: builder.mutation<CartItem, { product_id: string; quantity: number }>({
      query: (body) => ({
        url: '/cart',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Cart'],
    }),

    // Initiate Selected Items Checkout (Returns Chapa URL)
    checkoutCart: builder.mutation<CheckoutResponse, CheckoutRequest>({
      query: (body) => ({
        url: '/checkout',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Cart', 'Order'],
    }),

    // Verify Payment by Transaction Reference
    verifyPayment: builder.query<VerificationResponse, string>({
      query: (txRef) => `/verify/${txRef}`,
      providesTags: ['Order'],
    }),

    // Get Dynamic AI Upsell Recommendations
    getAiRecommendations: builder.query<Product[], void>({
      query: () => '/ai-recommendations',
      providesTags: ['Recommendations'],
    }),
  }),
});

export const {
  useAddToCartMutation,
  useCheckoutCartMutation,
  useVerifyPaymentQuery,
  useGetAiRecommendationsQuery,
} = orderApi;