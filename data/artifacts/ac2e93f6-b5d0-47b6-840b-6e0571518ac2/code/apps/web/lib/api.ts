
const BASE_URL = 'http://localhost:4000';
export const api = {
    get: (url: string) => fetch(`${BASE_URL}${url}`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(r => r.json()),
    post: (url: string, data: any) => fetch(`${BASE_URL}${url}`, { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify(data)
    }).then(r => r.json())
};
