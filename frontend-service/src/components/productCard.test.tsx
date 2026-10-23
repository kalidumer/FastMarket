import{render,screen,fireEvent} from '@testing-library/react';
import{describe,it,expect,vi} from 'vitest'
import{ProductCard}from './productCard'
import{Product } from '../types/productType'


const mockProduct: Product = {
  id: 'p1',
  title: 'Wireless Headphones',
  desc: 'High quality sound with noise cancellation',
  price: 2500,
  image: 'https://via.placeholder.com/150',
};


