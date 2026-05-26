import { api, setToken, clearToken } from './client';

export type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

type LoginResponse = { token: string; user: User };

export async function login(username: string, password: string): Promise<User> {
  const { data } = await api.post<LoginResponse>('/accounts/login/', { username, password });
  setToken(data.token);
  return data.user;
}

export async function signup(input: {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}): Promise<User> {
  const { data } = await api.post<User>('/accounts/signup/', input);
  // Auto-login après signup (réutilise les credentials)
  await login(input.username, input.password);
  return data;
}

export async function logout(): Promise<void> {
  try {
    await api.post('/accounts/logout/');
  } finally {
    clearToken();
  }
}

export async function me(): Promise<User> {
  const { data } = await api.get<User>('/accounts/me/');
  return data;
}
