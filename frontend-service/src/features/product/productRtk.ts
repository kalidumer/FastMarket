import {createApi,fetchBaseQuery} from "@reduxjs/toolkit/query/react"
import { Category, Product, SearchQueryParams } from "@/types/productType"


export const productApi=createApi({
    reducerPath:"productApi",
    baseQuery:fetchBaseQuery({
        baseUrl:"http://localhost:8007/api/products"
    }),
    endpoints:(builder)=>({
        getProducts:builder.query<Product[],void>({
            query:()=>"/",
        }),
        searchProducts:builder.query<Product[],SearchQueryParams>({
            query:(params)=>{
               const quaryparams=new URLSearchParams();
                if(params.q) quaryparams.append("q",params.q)
                if(params.category_id) quaryparams.append("category_id",params.category_id)
                if(params.min_price) quaryparams.append("min_price",params.min_price.toString())
                if(params.max_price) quaryparams.append("max_price",params.max_price.toString())
                    return `/search?${quaryparams.toString()}`
            }
        }),
        getCategories:builder.query<Category[],void>({
            query:()=>"/categories",
        }),
    })
})

export const {useGetProductsQuery,useSearchProductsQuery,useGetCategoriesQuery}=productApi;