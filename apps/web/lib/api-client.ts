import { API_BASE_URL } from './api-config';

const API_BASE = `${API_BASE_URL}/api`;

export const apiClient = {
    createProject: async (idea: string) => {
        const res = await fetch(`${API_BASE}/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idea }),
        });
        if (!res.ok) throw new Error('Failed to create project');
        return res.json();
    },

    getProject: async (id: string) => {
        const res = await fetch(`${API_BASE}/projects/${id}`);
        if (!res.ok) throw new Error('Project not found');
        return res.json();
    },

    getDocs: async (id: string) => {
        const res = await fetch(`${API_BASE}/projects/${id}/docs`);
        if (!res.ok) throw new Error('Docs not found');
        return res.json();
    },

    analyze: async (id: string) => {
        const res = await fetch(`${API_BASE}/projects/${id}/analyze`, { method: 'POST' });
        if (!res.ok) throw new Error('Analysis failed');
        return res.json();
    }
};
