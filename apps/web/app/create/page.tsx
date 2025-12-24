"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE_URL } from '@/lib/api-config';


export default function CreateProject() {
    const [idea, setIdea] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const res = await fetch(`${API_BASE_URL}/api/projects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ idea })
            });
            const data = await res.json();

            if (res.ok) {
                router.push(`/project/${data.id}`);
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error(error);
            alert('Failed to create project');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-black">
            <div className="z-10 w-full max-w-2xl">
                <h1 className="text-4xl font-bold mb-8 text-white text-center">Describe Your Dream App</h1>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="relative group">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-pink-600 to-purple-600 rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200"></div>
                        <textarea
                            value={idea}
                            onChange={(e) => setIdea(e.target.value)}
                            placeholder="I want to build a platform that..."
                            className="relative block w-full bg-black text-white border border-gray-800 rounded-lg p-6 text-xl min-h-[200px] focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder-gray-600 resize-none"
                            required
                        />
                    </div>

                    <div className="flex justify-center">
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="bg-white text-black px-12 py-4 rounded-full font-bold hover:bg-gray-200 transition text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <span className="animate-spin text-xl">◌</span> Creating...
                                </>
                            ) : (
                                'Launch Project 🚀'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </main>
    );
}
