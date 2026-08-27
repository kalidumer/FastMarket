export interface Product{
    id:string;
    title:string;
    desc:string;
    rating:number;
    reviewCount:number;
    price:number;
    image:string;
    category:string;
    isNew:boolean;
}

export interface Category{
    id:string;
    name:string;
    image:string;
    itemCount:number;
}

export interface SearchQueryParams{
    q?:string;
    category_id?:string;
    min_price?:number;
    max_price?:number;
}

export interface CartItem {
  id: number;
  user_id: string;
  product_id: string;
  quantity: number;
  product?: Product;
}

export interface CheckoutRequest{
    cart_items_ids:number[];
}

export interface CheckoutReponse{
    status:string;
    order_id:number;
    checkout_url:string;
    txt_ref:string;
}

export interface VerificationResponse{
    status:'paid' |'failed'|'pending';
    message:string;
    amount?:number;
}

