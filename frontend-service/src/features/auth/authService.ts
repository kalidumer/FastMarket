import api from "../../utils/api";
import { AuthResponse, LoginCredentials, RegisterCredentials, UserProfile } from "../../types/auth";

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>("/auth/login", {
      email: credentials.email,
      password: credentials.password,
    });
    return response.data;
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