'use client';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { Project, GeneratedDoc, UIAsset } from '@/types';
import ReactMarkdown from 'react-markdown';
import { API_BASE_URL } from '@/lib/api-config';


export default function ProjectDashboard({ params }: { params: { id: string } }) {
    const [project, setProject] = useState<Project | null>(null);
    const [docs, setDocs] = useState<GeneratedDoc[]>([]);
    const [visuals, setVisuals] = useState<UIAsset[]>([]);
    const [activeTab, setActiveTab] = useState<'docs' | 'visuals' | 'code'>('docs');
    const [loadingDesign, setLoadingDesign] = useState(false);

    useEffect(() => {
        // Initial fetch
        apiClient.getProject(params.id).then(setProject).catch(console.error);
        apiClient.getDocs(params.id).then(setDocs).catch(console.error);
        apiClient.getVisuals(params.id).then(setVisuals).catch(console.error);

        // Poll for status updates
        const interval = setInterval(async () => {
            try {
                const p = await apiClient.getProject(params.id);
                setProject(p);
                if (p.status === 'DESIGNED' && visuals.length === 0) {
                    const v = await apiClient.getVisuals(params.id);
                    setVisuals(v);
                }
            } catch (e) {
                console.error(e);
            }
        }, 2000);
        return () => clearInterval(interval);
    }, [params.id]);

    if (!project) return <div className="min-h-screen flex items-center justify-center">Loading Project...</div>;

    return (
        <div className="min-h-screen flex flex-col">
            <header className="border-b bg-neutral-900/50 backdrop-blur p-4 flex justify-between items-center sticky top-0 z-50">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center font-bold">
                        {project.name.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                        <h1 className="font-bold text-lg">{project.name}</h1>
                        <p className="text-xs text-muted-foreground">{project.id}</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-mono ${getStatusColor(project.status)}`}>
                        {project.status}
                    </span>
                </div>
            </header>

            <main className="flex-1 p-6">
                <div className="max-w-7xl mx-auto grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">
                    {/* Sidebar */}
                    <div className="col-span-3 border rounded-xl bg-card/50 p-4 space-y-2">
                        <button
                            onClick={() => setActiveTab('docs')}
                            className={`w-full text-left px-4 py-2 rounded-lg transition ${activeTab === 'docs' ? 'bg-primary/20 text-primary' : 'hover:bg-neutral-800'}`}
                        >
                            Documentation
                        </button>
                        <button
                            onClick={() => setActiveTab('visuals')}
                            className={`w-full text-left px-4 py-2 rounded-lg transition ${activeTab === 'visuals' ? 'bg-primary/20 text-primary' : 'hover:bg-neutral-800'}`}
                        >
                            Visual Design
                        </button>
                        <button
                            onClick={() => setActiveTab('code')}
                            className={`w-full text-left px-4 py-2 rounded-lg transition ${activeTab === 'code' ? 'bg-primary/20 text-primary' : 'hover:bg-neutral-800'}`}
                        >
                            Codebase
                        </button>
                    </div>

                    {/* Main Content Area */}
                    <div className="col-span-9 border rounded-xl bg-neutral-950 p-6 overflow-auto font-mono text-sm relative">
                        {activeTab === 'docs' && (
                            <div className="space-y-8 max-w-4xl mx-auto">
                                <h2 className="text-2xl font-bold font-sans mb-4">Project Documentation</h2>
                                {docs.length === 0 ? (
                                    <div className="p-8 border border-dashed rounded-lg border-neutral-800 text-neutral-500 text-center">
                                        <p>Analyzing idea...</p>
                                    </div>
                                ) : (
                                    docs.map(doc => (
                                        <div key={doc.id} className="mb-8 p-6 bg-card rounded-xl border">
                                            <h3 className="text-xl font-bold text-primary mb-4">{doc.title}</h3>
                                            <div className="prose prose-invert max-w-none whitespace-pre-wrap font-sans text-neutral-300">
                                                {doc.content}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        )}
                        {activeTab === 'visuals' && (
                            <div className="flex flex-col h-full">
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-2xl font-bold font-sans">Visual Design</h2>
                                    <button
                                        onClick={async () => {
                                            setLoadingDesign(true);
                                            await fetch(`${API_BASE_URL}/api/projects/${params.id}/design`, { method: 'POST' });
                                            // Status polling will pick up the results
                                        }}
                                        disabled={loadingDesign || visuals.length > 0}
                                        className="bg-primary text-primary-foreground px-4 py-2 rounded hover:opacity-90 disabled:opacity-50"
                                    >
                                        {loadingDesign ? 'Generating...' : visuals.length > 0 ? 'Design Ready' : 'Generate Visuals'}
                                    </button>
                                </div>

                                {visuals.length > 0 ? (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {visuals.map(v => (
                                            <div key={v.id} className="border rounded-xl overflow-hidden bg-neutral-900 flex flex-col group">
                                                <div className="relative aspect-video bg-black overflow-hidden">
                                                    <img
                                                        src={v.imageUrl}
                                                        alt={v.screenName}
                                                        className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition duration-500 group-hover:scale-105"
                                                    />
                                                </div>
                                                <div className="p-4 flex flex-col gap-3">
                                                    <div>
                                                        <h3 className="font-bold text-base text-white">{v.screenName}</h3>
                                                        <p className="text-xs text-neutral-400 line-clamp-1">{v.description}</p>
                                                    </div>
                                                    <div className="flex gap-2">
                                                        {v.wireframeKey && (
                                                            <a
                                                                href={`${API_BASE_URL}/api/projects/${params.id}/wireframes/${v.wireframeKey}.html`}
                                                                target="_blank"
                                                                className="flex-1 text-center py-2 bg-neutral-800 hover:bg-neutral-700 text-xs font-bold rounded-lg transition"
                                                            >
                                                                Live Wireframe
                                                            </a>
                                                        )}
                                                        {v.uiKey && (
                                                            <a
                                                                href={`${API_BASE_URL}/api/projects/${params.id}/ui/${v.uiKey}.html`}
                                                                target="_blank"
                                                                className="flex-1 text-center py-2 bg-blue-600 hover:bg-blue-500 text-xs font-bold rounded-lg transition"
                                                            >
                                                                Live UI
                                                            </a>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="flex-1 flex flex-col items-center justify-center text-neutral-500 border border-dashed rounded-xl p-12">
                                        <div className="w-16 h-16 bg-neutral-900 rounded-full flex items-center justify-center mb-4">
                                            <svg className="w-8 h-8 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                        </div>
                                        <p className="font-sans">No visuals generated yet.</p>
                                        <p className="text-xs mt-2 font-sans opacity-60">Click "Generate Visuals" to start the AI design process.</p>
                                    </div>
                                )}
                            </div>
                        )}
                        {activeTab === 'code' && (
                            <div className="flex flex-col items-center justify-center h-full text-neutral-500">
                                <p>Waiting for Sign-off on Design to generate Code.</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}

function getStatusColor(status: string) {
    switch (status) {
        case 'NEW': return 'bg-blue-500/20 text-blue-400';
        case 'ANALYSIS': return 'bg-yellow-500/20 text-yellow-400';
        case 'COMPLETED': return 'bg-green-500/20 text-green-400';
        default: return 'bg-neutral-500/20 text-neutral-400';
    }
}
