import{createAsyncThunk, createSlice, PayloadAction} from '@reduxjs/toolkit';
import { AuthState, LoginCredentials, RegisterCredentials, UserProfile } from '../../types/auth';
import {authService} from './authService';

const initialState:AuthState={
   user:null,
   token:localStorage.getItem('token'),
   loading:false,
   error:null
}

export const loginUser=createAsyncThunk<string , LoginCredentials, {rejectValue:string}>(
    'user/loginUser',
    async(credentials,{rejectWithValue}) =>{
        try{
            const data=await authService.login(credentials);
            localStorage.setItem('token',data.access_token)
            return data.access_token;
        }

        catch(err:any){
            return rejectWithValue(err.response?.data?.detail || 'Invalid email or password');
        }
    }
)

export const registerUser=createAsyncThunk<UserProfile,RegisterCredentials,{rejectValue:string}>(
    'user/registerUser',
    async(credentials,{rejectWithValue}) =>{
        try {
            return await authService.register(credentials);
        } catch (err:any) {
            return rejectWithValue(err.response?.data?.detail || 'Registeration fail.Try again')
        }
    }
)

export const fetchCurrentUser=createAsyncThunk<UserProfile ,void ,{rejectValue:string}>(
'user/fetchCurrentUser',
async(_,{rejectWithValue}) => {
    try {
        return await authService.getProfile();
    } catch (err:any) {
        return rejectWithValue(err.response?.data.detail || 'Session expire');  
    }
}
);

const authSlice=createSlice({
    name:'auth',
    initialState,
    reducers:{
        logout:(state)=>{
            localStorage.removeItem('token');
            state.user=null;
            state.token=null;
            state.error=null;
            state.loading=false;
        },
        clearAuthError:(state)=>{
            state.error=null;
        },
    },

    extraReducers:(builder)=>{
        builder
        // fetching login lifecycle
        .addCase(loginUser.pending,(state) => {
            state.loading=true;
            state.error=null;
        })
        .addCase(loginUser.fulfilled,(state,action:PayloadAction<string>)=>{
            state.loading=false;
            state.token=action.payload;
        })
        .addCase(loginUser.rejected,(state,action)=>{
            state.loading=false;
            state.error=action.payload || 'An error occurred during sign in'
        })

        //fetching Profile Lifecycle

        .addCase(fetchCurrentUser.fulfilled,(state,action:PayloadAction<UserProfile>) =>{
            state.user=action.payload;
        })
        .addCase(fetchCurrentUser.rejected,(state)=>{
            localStorage.removeItem('token');
            state.token=null;
            state.user=null;
        })
    }
})

export const {logout,clearAuthError}=authSlice.actions;
export default authSlice.reducer;