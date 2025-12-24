'use client';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { Project, GeneratedDoc, UIAsset } from '@idea-to-deploy/types';
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

        // Poll for status updates
        const interval = setInterval(async () => {
            try {
                const p = await apiClient.getProject(params.id);
                setProject(p);
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
                    <span className={`px-2 py-1 rounded-full text-xs font-mono \${getStatusColor(project.status)}`}>
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
                            className={`w-full text-left px-4 py-2 rounded-lg transition \${activeTab === 'docs' ? 'bg-primary/20 text-primary' : 'hover:bg-neutral-800'}`}
                        >
                            Documentation
                        </button>
                        <button
                            onClick={() => setActiveTab('visuals')}
                            className={`w-full text-left px-4 py-2 rounded-lg transition \${activeTab === 'visuals' ? 'bg-primary/20 text-primary' : 'hover:bg-neutral-800'}`}
                        >
                            Visual Design
                        </button>
                        <button
                            onClick={() => setActiveTab('code')}
                            className={`w-full text-left px-4 py-2 rounded-lg transition \${activeTab === 'code' ? 'bg-primary/20 text-primary' : 'hover:bg-neutral-800'}`}
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
                                            // trigger design
                                            await fetch(`${API_BASE_URL}/api/projects/${params.id}/design`, { method: 'POST' });
                                            // Mock fetch back for now or wait for poll (if we persisted)
                                            // For demo:
                                            setTimeout(() => {
                                                setVisuals([
                                                    {
                                                        id: '1', projectId: params.id, screenName: 'Dashboard', description: 'Main Dashboard',
                                                        promptUsed: 'Dashboard', imageUrl: 'https://placehold.co/800x600/1a1a1a/FFF?text=Dashboard'
                                                    },
                                                    {
                                                        id: '2', projectId: params.id, screenName: 'Mobile App', description: 'Mobile View',
                                                        promptUsed: 'Mobile', imageUrl: 'https://placehold.co/400x800/1a1a1a/FFF?text=Mobile+View'
                                                    }
                                                ]);
                                                setLoadingDesign(false);
                                            }, 2000);
                                        }}
                                        disabled={loadingDesign || visuals.length > 0}
                                        className="bg-primary text-primary-foreground px-4 py-2 rounded hover:opacity-90 disabled:opacity-50"
                                    >
                                        {loadingDesign ? 'Generating...' : visuals.length > 0 ? 'Regenerate' : 'Generate Visuals'}
                                    </button>
                                </div>

                                {visuals.length > 0 ? (
                                    <div className="grid grid-cols-2 gap-4">
                                        {visuals.map(v => (
                                            <div key={v.id} className="border rounded-lg overflow-hidden bg-black">
                                                <img src={v.imageUrl} alt={v.screenName} className="w-full h-auto opacity-90 hover:opacity-100 transition" />
                                                <div className="p-2 text-xs text-neutral-400 border-t border-neutral-900">{v.screenName}</div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="flex-1 flex items-center justify-center text-neutral-500 border border-dashed rounded-lg mx-auto w-full">
                                        <p>No visuals generated yet. Click Generate to start AI Designer.</p>
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
