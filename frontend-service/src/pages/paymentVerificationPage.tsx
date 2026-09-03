import React from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useVerifyPaymentQuery } from '../features/product/orderapi';
import { AiRecommendations } from '../components/AiRecommendations';

export const PaymentVerifyPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const txRef = searchParams.get('tx_ref') || '';
  const navigate = useNavigate();

  const { data, isLoading, isError } = useVerifyPaymentQuery(txRef, {
    skip: !txRef,
  });

  if (!txRef) {
    return (
      <div className="max-w-md mx-auto mt-12 p-6 text-center border rounded-lg bg-red-50">
        <h2 className="text-red-700 font-bold text-lg">Invalid Callback</h2>
        <p className="text-sm text-red-600 mt-2">No transaction reference provided.</p>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto mt-12 p-6 bg-white border rounded-xl shadow-sm text-center">
      {isLoading && (
        <p className="text-gray-600 font-medium">Verifying transaction with Chapa...</p>
      )}

      {isError && (
        <div className="text-red-600">
          <h2 className="text-xl font-bold">Verification Error</h2>
          <p className="mt-2 text-sm">Could not verify transaction status.</p>
        </div>
      )}

      {data?.status === 'paid' && (
        <div>
          <div className="w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto text-2xl font-bold mb-3">
            ✓
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Payment Successful!</h2>
          <p className="text-gray-600 text-sm mt-1">{data.message}</p>

          <button
            onClick={() => navigate('/')}
            className="mt-6 px-5 py-2 bg-black text-white text-sm font-medium rounded-lg hover:bg-gray-800"
          >
            Continue Shopping
          </button>

          {/* Render AI Upsell Recommendations after purchase */}
          <AiRecommendations />
        </div>
      )}

      {data?.status === 'failed' && (
        <div>
          <div className="w-12 h-12 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto text-2xl font-bold mb-3">
            ✕
          </div>
          <h2 className="text-2xl font-bold text-gray-900">Payment Failed</h2>
          <p className="text-gray-600 text-sm mt-1">{data.message}</p>
          <button
            onClick={() => navigate('/cart')}
            className="mt-6 px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
          >
            Return to Cart
          </button>
        </div>
      )}
    </div>
  );
};