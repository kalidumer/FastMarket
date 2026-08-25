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