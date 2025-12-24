const getBaseUrl = () => {
    const url = process.env.NEXT_PUBLIC_API_URL;
    if (!url) return 'http://localhost:4000';
    if (url.startsWith('http')) return url;
    return `https://${url}`;
};

export const API_BASE_URL = getBaseUrl();
