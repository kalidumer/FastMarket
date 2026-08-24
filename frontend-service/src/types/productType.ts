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