export interface LoginCredentials {
  email: string;
  // Kept clean for secure structural parsing
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
}

export interface AuthState {
  user: UserProfile | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}