import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import authReducer from '../features/auth/authSlice';
import { productApi } from '../features/product/productRtk';
// import cartReducer from '../features/cart/cartSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    // cart: cartReducer,
  [productApi.reducerPath]:productApi.reducer},

  middleware:(getDefaulMiddleware)=>getDefaulMiddleware().concat(productApi.middleware),
});

// Derive structural application types straight from the store schema
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Expert Pattern: Custom typed hook abstractions to bypass generic hook bugs
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;