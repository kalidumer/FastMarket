import { CartItem } from "@/types/productType";
import { createApi,fetchBaseQuery, RootState} from "@reduxjs/toolkit/query";

export const orderApi=createApi({
    reducerPath:'orderApi',
    baseQuery:fetchBaseQuery({
        baseUrl:'http://localhost:8007/api/order',
        prepareHeaders:(headers,{getState})=>{
            const token=(getState as RootState).auth.token;
        }
    })
})
