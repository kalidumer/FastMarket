import React, { useState } from 'react';
import { Product } from '../types/productType';

interface ProductCardProps {
  product: Product;
  // Make addToCart return a Promise so the card can manage its local async state
  addToCart: (product: Product) => Promise<void> | void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, addToCart }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleAdd = async () => {
    if (isSubmitting) return;

    try {
      setIsSubmitting(true);
      await addToCart(product);
      
      // Flash brief success state
      setIsSuccess(true);
      setTimeout(() => setIsSuccess(false), 1500);
    } catch (error) {
      console.error(`Failed to add product ${product.id}:`, error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
      {/* Product Image */}
      <div>
        <div className="relative aspect-square w-full overflow-hidden rounded-xl bg-gray-100 dark:bg-gray-800">
          <img
            src={product.image || 'https://via.placeholder.com/300'}
            alt={product.title}
            className="h-full w-full object-cover object-center transition-transform duration-300 group-hover:scale-105"
          />
        </div>

        {/* Product Details */}
        <div className="mt-4 space-y-1">
          <h3 className="line-clamp-1 text-sm font-bold text-gray-900 dark:text-white">
            {product.title}
          </h3>
          <p className="line-clamp-2 text-xs text-gray-500 dark:text-gray-400">
            {product.description}
          </p>
        </div>
      </div>

      {/* Price & Action Button */}
      <div className="mt-4 pt-2 flex items-center justify-between border-t border-gray-100 dark:border-gray-800">
        <div>
          <span className="text-xs text-gray-400 block font-medium">Price</span>
          <span className="text-base font-black text-indigo-600 dark:text-indigo-400">
            ETB {product.price?.toLocaleString()}
          </span>
        </div>

        <button
          type="button"
          onClick={handleAdd}
          disabled={isSubmitting}
          className={`relative flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
            isSuccess
              ? 'bg-emerald-600 text-white'
              : 'bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white disabled:bg-indigo-400 disabled:cursor-not-allowed'
          }`}
        >
          {isSubmitting ? (
            <>
              {/* Spinner */}
              <svg
                className="h-4 w-4 animate-spin text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <span>Adding...</span>
            </>
          ) : isSuccess ? (
            <>
              {/* Checkmark Icon */}
              <svg
                className="h-4 w-4 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2.5"
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span>Added!</span>
            </>
          ) : (
            <>
              {/* Cart Icon */}
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              <span>Add to Cart</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};