const getBaseUrl = () => {
    const url = process.env.NEXT_PUBLIC_API_URL;
    if (!url) return 'http://127.0.0.1:4000';
    if (url.startsWith('http')) return url;
    return `https://${url}`;
};

export const API_BASE_URL = getBaseUrl();
