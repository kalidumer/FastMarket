import React from 'react';
import { useGetAiRecommendationsQuery, useAddToCartMutation } from '../features/product/orderapi';

export const AiRecommendations: React.FC = () => {
  const { data: recommendations = [], isLoading } = useGetAiRecommendationsQuery();
  const [addToCart, { isLoading: isAdding }] = useAddToCartMutation();

  if (isLoading || recommendations.length === 0) return null;

  return (
    <div className="mt-10 border-t pt-6 text-left">
      <h3 className="text-lg font-bold text-gray-900 mb-4">
        Recommended For You (AI Suggestions)
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {recommendations.map((product) => (
          <div
            key={product.id}
            className="border p-4 rounded-lg bg-gray-50 flex flex-col justify-between"
          >
            <div>
              <h4 className="font-semibold text-sm text-gray-800 line-clamp-1">
                {product.title}
              </h4>
              <p className="text-xs text-gray-500 mt-1">
                ETB {product.price.toFixed(2)}
              </p>
            </div>
            <button
              onClick={() => addToCart({ product_id: product.id, quantity: 1 })}
              disabled={isAdding}
              className="mt-3 w-full py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition"
            >
              Add to Cart
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};