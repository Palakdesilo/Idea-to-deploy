
import { API_BASE_URL } from './api-config';

const getHeaders = () => {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
};

async function request(endpoint: string, options: RequestInit = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

    const res = await fetch(url, {
        ...options,
        headers: {
            ...getHeaders(),
            ...options.headers,
        },
    });

    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `API Error: ${res.statusText}`);
    }

    return res.json();
}

export const api = {
    get: <T = any>(endpoint: string) => request(endpoint, { method: 'GET' }) as Promise<T>,
    post: <T = any>(endpoint: string, data: any) => request(endpoint, { method: 'POST', body: JSON.stringify(data) }) as Promise<T>,
    put: <T = any>(endpoint: string, data: any) => request(endpoint, { method: 'PUT', body: JSON.stringify(data) }) as Promise<T>,
    delete: <T = any>(endpoint: string) => request(endpoint, { method: 'DELETE' }) as Promise<T>,
    patch: <T = any>(endpoint: string, data: any) => request(endpoint, { method: 'PATCH', body: JSON.stringify(data) }) as Promise<T>,
};

export default api;
