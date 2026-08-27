import { CartItem } from "@/types/productType";
import { createApi,fetchBaseQuery, RootState} from "@reduxjs/toolkit/query";

export const cartApi=createApi({
    reducerPath:'cartApi',
    baseQuery:fetchBaseQuery({
        baseUrl:'http://localhost:8007/api/cart',
        prepareHeaders:(headers,{getState})=>{
            const token=(getState() as RootState).auth.token;
            if(token){
                headers.set('authorization',`Bearer ${token}`);
            }return headers
        }
    }),
    tagTypes:'CART',
endpoints: (builder) => ({
    getCart: builder.query<CartItem[], void>({
      query: () => '/',
      providesTags: ['Cart'],
    })
    }
}),
