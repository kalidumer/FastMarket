import React, { useState } from 'react';
import { useCheckoutCartMutation } from '../features/product/orderapi';
import { CartItem } from '../types/productType';

interface CartPageProps {
  cartItems: CartItem[];
}

export const CartPage: React.FC<CartPageProps> = ({ cartItems }) => {
  const [selectedIds, setSelectedIds] = useState<number[]>(
    cartItems.map((item) => item.id)
  );

  const [checkoutCart, { isLoading: isCheckingOut }] = useCheckoutCartMutation();

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleCheckout = async () => {
    if (selectedIds.length === 0) return;
    try {
      const response = await checkoutCart({ cart_item_ids: selectedIds }).unwrap();
      // Redirect to Chapa Payment Gateway URL
      window.location.href = response.checkout_url;
    } catch (err: any) {
      alert(err?.data?.detail || 'Checkout process failed.');
    }
  };

  const selectedTotal = cartItems
    .filter((item) => selectedIds.includes(item.id))
    .reduce((sum, item) => sum + (item.product?.price || 0) * item.quantity, 0);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6 text-gray-900">Shopping Cart</h1>

      {cartItems.length === 0 ? (
        <p className="text-gray-500">Your cart is empty.</p>
      ) : (
        <div className="space-y-4">
          {cartItems.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-4 border rounded-lg bg-white shadow-sm"
            >
              <input
                type="checkbox"
                checked={selectedIds.includes(item.id)}
                onChange={() => toggleSelect(item.id)}
                className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
              />
              <div className="flex-1 ml-4">
                <h3 className="font-semibold text-gray-800">
                  {item.product?.title || `Product #${item.product_id}`}
                </h3>
                <p className="text-sm text-gray-500">
                  ETB {item.product?.price?.toFixed(2)} × {item.quantity}
                </p>
              </div>
              <span className="font-bold text-gray-900">
                ETB {((item.product?.price || 0) * item.quantity).toFixed(2)}
              </span>
            </div>
          ))}

          {/* Checkout Banner */}
          <div className="mt-8 p-6 bg-gray-50 rounded-lg flex justify-between items-center border">
            <div>
              <p className="text-sm text-gray-500">Selected Subtotal</p>
              <p className="text-2xl font-bold text-gray-900">
                ETB {selectedTotal.toFixed(2)}
              </p>
            </div>
            <button
              onClick={handleCheckout}
              disabled={selectedIds.length === 0 || isCheckingOut}
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {isCheckingOut ? 'Redirecting to Chapa...' : 'Proceed to Checkout'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};