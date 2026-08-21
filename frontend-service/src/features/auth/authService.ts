import api from "../../utils/api";
import { AuthResponse, LoginCredentials, RegisterCredentials, UserProfile } from "../../types/auth";

export const authService={

//     login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
//     const payload = new URLSearchParams();
//     payload.append('username', credentials.email);
//     payload.append('password', credentials.password);

//     const response = await api.post<AuthResponse>('/auth/login', payload, {
//       headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
//     });
//     return response.data;
//     console.log("frealem login response:", response.data);
//   }
    login:async(credentials:LoginCredentials):Promise<AuthResponse> =>{
        const payload=new URLSearchParams();
        payload.append('username',credentials.email);
        payload.append('password',credentials.password);
        console.log();
     const response = await api.post<AuthResponse>('/auth/login', payload);
        console.log("frealem login response:", response.data);
        return response.data
    },

    register:async(credentials:RegisterCredentials):Promise<UserProfile> => {
        const response=await api.post<UserProfile>('/auth/register',{
            email:credentials.email,
            password:credentials.password,
            full_name:credentials.full_name,
        });
        return response.data;
    },

    getProfile:async():Promise<UserProfile> =>{
        const response=await api.get<UserProfile>('/auth/profile')
        return response.data
    }
}