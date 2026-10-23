import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProductCard } from './productCard';
import { Product } from '../types/productType';

const mockProduct: Product = {
  id: 'p1',
  title: 'Wireless Headphones',
  desc: 'High quality sound with noise cancellation',
  price: 2500,
  image: 'https://via.placeholder.com/150',
};

describe('ProductCard Component', () => {
  it('renders product title and price correctly', () => {
    render(<ProductCard product={mockProduct} addToCart={() => {}} />);
    
    expect(screen.getByText('Wireless Headphones')).toBeInTheDocument();
    expect(screen.getByText(/2,500/)).toBeInTheDocument();
  });

  it('calls addToCart handler when button is clicked', () => {
    // Create a mock tracking function
    const handleAddToCart = vi.fn();

    render(<ProductCard product={mockProduct} addToCart={handleAddToCart} />);
    
    const button = screen.getByRole('button', { name: /add to cart/i });
    fireEvent.click(button);

    // Verify callback was fired with the correct product object
    expect(handleAddToCart).toHaveBeenCalledTimes(1);
    expect(handleAddToCart).toHaveBeenCalledWith(mockProduct);
  });
});