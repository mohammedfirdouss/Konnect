import { ProductInterface } from './marketplace';

export interface OrderDto {
  listing_id: number;
  quantity: number;
  delivery_address: string;
  notes: string;
}

export interface CartItem {
  id: string;
  product: ProductInterface;
  quantity: number;
}
