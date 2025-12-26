"use client";
import Link from 'next/link';
import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
    Search, Filter, ChevronDown, MoreVertical,
    Folders, CheckCircle2, Activity, Clock,
    ArrowDown, Trash2, ExternalLink, LayoutGrid,
    Layout, Settings, History, Info, Plus, ChevronRight,
    RotateCcw, AlertCircle, FileText
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_BASE_URL } from '@/lib/api-config';


export default function Dashboard() {
    const [projects, setProjects] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');
    const [filter, setFilter] = useState('All Projects');
    const router = useRouter();
    const checkApiStatus = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/health`);
            setApiStatus(res.ok ? 'online' : 'offline');
        } catch {
            setApiStatus('offline');
        }
    };

    const fetchProjects = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/projects`);
            if (res.ok) {
                const data = await res.json();
                setProjects(data);
                setApiStatus('online');
            } else {
                setApiStatus('offline');
            }
        } catch (err) {
            console.error(err);
            setApiStatus('offline');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkApiStatus();
        fetchProjects();
        // Periodically check API status
        const interval = setInterval(checkApiStatus, 10000);
        return () => clearInterval(interval);
    }, []);

    const stats = useMemo(() => {
        const completed = projects.filter(p => p.status === 'COMPLETED').length;
        const processing = projects.filter(p => ['ANALYSIS', 'DESIGN', 'CODING', 'PLANNING', 'DESIGNED'].includes(p.status)).length;
        const failed = projects.filter(p => p.status === 'FAILED').length;
        return {
            all: projects.length,
            completed,
            processing,
            failed
        };
    }, [projects]);

    const filteredProjects = useMemo(() => {
        if (filter === 'All Projects') return projects;
        if (filter === 'Completed') return projects.filter(p => p.status === 'COMPLETED');
        if (filter === 'Processing') return projects.filter(p => ['ANALYSIS', 'DESIGN', 'CODING', 'PLANNING', 'DESIGNED'].includes(p.status));
        if (filter === 'Failed') return projects.filter(p => p.status === 'FAILED');
        return projects;
    }, [projects, filter]);

    const getProgress = (status: string) => {
        switch (status) {
            case 'COMPLETED': return 100;
            case 'CODING': return 75;
            case 'DESIGNED': return 65;
            case 'DESIGN': return 50;
            case 'PLANNING': return 40;
            case 'ANALYSIS': return 25;
            case 'NEW': return 10;
            case 'FAILED': return 0;
            default: return 0;
        }
    };

    const ProjectCard = ({ project }: { project: any }) => {
        const isProcessing = ['ANALYSIS', 'DESIGN', 'CODING', 'PLANNING', 'DESIGNED', 'NEW'].includes(project.status);
        const isCompleted = project.status === 'COMPLETED';
        const isFailed = project.status === 'FAILED';
        const progress = getProgress(project.status);

        return (
            <motion.div
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                onClick={() => router.push(`/project/${project.id}?view=${isCompleted ? 'Results' : 'Pipeline'}`)}
                className="bg-[#1e293b]/40 backdrop-blur-md border border-slate-800 rounded-[2rem] p-8 hover:bg-[#1e293b]/60 transition-all duration-300 flex flex-col h-[380px] group relative overflow-hidden cursor-pointer"
            >
                {/* Background Glow */}
                <div className={`absolute top-0 right-0 w-32 h-32 blur-[80px] rounded-full -mr-16 -mt-16 transition-all duration-500 opacity-20 ${isCompleted ? 'bg-emerald-500' : isProcessing ? 'bg-blue-500' : 'bg-rose-500'
                    }`} />

                <div className="flex justify-between items-start mb-6">
                    <div className="flex-1">
                        <h3 className="text-2xl font-bold text-white group-hover:text-blue-400 transition-colors line-clamp-1 mb-2">{project.name}</h3>
                        <p className="text-slate-400 text-sm line-clamp-2 leading-relaxed">{project.description}</p>
                    </div>
                    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ring-1 ${isCompleted ? 'text-emerald-400 bg-emerald-500/10 ring-emerald-500/20' :
                        isProcessing ? 'text-blue-400 bg-blue-500/10 ring-blue-500/20' :
                            'text-rose-400 bg-rose-500/10 ring-rose-500/20'
                        }`}>
                        {isProcessing && <RotateCcw className="w-3 h-3 animate-spin" />}
                        {isCompleted && <CheckCircle2 className="w-3 h-3" />}
                        {isFailed && <AlertCircle className="w-3 h-3" />}
                        {project.status === 'DESIGNED' ? 'Processing' : project.status}
                    </div>
                </div>

                <div className="mt-auto space-y-8">
                    {isProcessing && (
                        <div className="space-y-3">
                            <div className="flex justify-between items-end">
                                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Progress</span>
                                <span className="text-xs font-black text-white">{progress}%</span>
                            </div>
                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progress}%` }}
                                    className="h-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                                />
                            </div>
                        </div>
                    )}

                    <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Created</span>
                            <span className="text-xs font-bold text-slate-300">
                                {new Date(project.createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                            </span>
                        </div>

                        {isCompleted ? (
                            <Link href={`/project/${project.id}?view=Results`}>
                                <button className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all font-bold text-sm shadow-lg shadow-blue-500/20 flex items-center gap-2">
                                    View Results
                                    <ChevronRight className="w-4 h-4" />
                                </button>
                            </Link>
                        ) : isProcessing ? (
                            <Link href={`/project/${project.id}?view=Pipeline`}>
                                <button className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-white rounded-xl transition-all font-bold text-sm shadow-lg shadow-emerald-500/20 flex items-center gap-2">
                                    View Progress
                                    <ChevronRight className="w-4 h-4" />
                                </button>
                            </Link>
                        ) : (
                            <Link href={`/project/${project.id}?view=Pipeline`}>
                                <button className="px-6 py-3 bg-rose-600 hover:bg-rose-500 text-white rounded-xl transition-all font-bold text-sm shadow-lg shadow-rose-500/20 flex items-center gap-2">
                                    Retry
                                    <RotateCcw className="w-4 h-4" />
                                </button>
                            </Link>
                        )}
                    </div>
                </div>
            </motion.div>
        );
    };

    const latestProject = useMemo(() => {
        if (projects.length === 0) return null;
        return projects.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())[0];
    }, [projects]);

    return (
        <main className="min-h-screen bg-[#020617] text-slate-100 font-sans selection:bg-blue-500/30">
            {/* Top Navigation */}
            <nav className="border-b border-slate-800 bg-[#020617]/80 backdrop-blur-md sticky top-0 z-40">
                <div className="max-w-[1400px] mx-auto px-10 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-8">
                        <Link href="/" className="flex items-center gap-2.5">
                            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                                <Layout className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold tracking-tight">Idea-to-deploy</span>
                        </Link>
                        <div className="hidden md:flex items-center gap-1">
                            {[
                                { id: 'Dashboard', icon: LayoutGrid, path: '/', active: true },
                                { id: 'Pipeline', icon: Activity, path: latestProject ? `/project/${latestProject.id}?view=Pipeline` : '#' },
                                { id: 'Results', icon: FileText, path: latestProject ? `/project/${latestProject.id}?view=Results` : '#' },
                                { id: 'History', icon: History, path: '/projects' },
                            ].map((item) => (
                                <Link
                                    key={item.id}
                                    href={item.path}
                                    className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-all text-sm font-bold ${item.active
                                        ? 'bg-blue-600/10 text-blue-400'
                                        : item.path === '#' ? 'text-slate-600 cursor-not-allowed' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                                        }`}
                                >
                                    <item.icon className="w-4 h-4" />
                                    {item.id}
                                </Link>
                            ))}
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/50 border border-slate-800">
                            <div className={`w-1.5 h-1.5 rounded-full ${apiStatus === 'online' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]' :
                                apiStatus === 'offline' ? 'bg-rose-500 animate-pulse' : 'bg-slate-500'
                                }`} />
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                API: {apiStatus}
                            </span>
                        </div>
                        <Link href="/create">
                            <button className="flex items-center gap-2 bg-white text-black px-4 py-2 rounded-lg font-bold hover:bg-slate-200 transition text-sm">
                                <Plus className="w-4 h-4" />
                                New Project
                            </button>
                        </Link>
                        <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-white">
                            <Settings className="w-5 h-5" />
                        </button>
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600" />
                    </div>
                </div>
            </nav>

            <div className="max-w-[1400px] mx-auto px-10 py-12">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
                    <div>
                        <h1 className="text-4xl font-black mb-3 tracking-tight">Recent Projects</h1>
                        <p className="text-slate-400 text-lg font-medium">Track and manage your product development pipelines</p>
                    </div>
                    <Link href="/projects" className="flex items-center gap-2 text-blue-400 hover:text-blue-300 font-bold transition-all group">
                        View All Projects
                        <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                </div>

                {/* Filter Tabs */}
                <div className="flex items-center gap-3 mb-10 overflow-x-auto pb-2 scrollbar-hide">
                    {[
                        { id: 'All Projects', count: stats.all },
                        { id: 'Completed', count: stats.completed },
                        { id: 'Processing', count: stats.processing },
                        { id: 'Failed', count: stats.failed }
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setFilter(tab.id)}
                            className={`flex items-center gap-3 px-6 py-3 rounded-2xl transition-all font-bold text-sm whitespace-nowrap ${filter === tab.id
                                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                                : 'bg-slate-900/50 text-slate-400 border border-slate-800 hover:bg-slate-800'
                                }`}
                        >
                            {tab.id}
                            <span className={`px-2 py-0.5 rounded-lg text-xs ${filter === tab.id ? 'bg-white/20' : 'bg-slate-800 text-slate-500'}`}>
                                {tab.count}
                            </span>
                        </button>
                    ))}
                </div>

                {/* Projects Grid */}
                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="h-[380px] bg-[#1e293b]/20 border border-slate-800 rounded-[2rem] animate-pulse" />
                        ))}
                    </div>
                ) : filteredProjects.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        <AnimatePresence mode="popLayout">
                            {filteredProjects.map((project) => (
                                <ProjectCard key={project.id} project={project} />
                            ))}
                        </AnimatePresence>
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center py-32 bg-slate-900/20 rounded-[3rem] border-2 border-dashed border-slate-800">
                        <div className="w-20 h-20 bg-slate-800/50 rounded-[2rem] flex items-center justify-center mb-6">
                            {apiStatus === 'offline' ? (
                                <AlertCircle className="w-10 h-10 text-rose-500" />
                            ) : (
                                <Folders className="w-10 h-10 text-slate-600" />
                            )}
                        </div>
                        <h3 className="text-2xl font-bold text-slate-300 mb-2">
                            {apiStatus === 'offline' ? 'API Connection Lost' : 'No projects found'}
                        </h3>
                        <p className="text-slate-500 mb-8 max-w-sm text-center">
                            {apiStatus === 'offline'
                                ? 'We cannot reach the backend server. Please make sure the API is running on port 4000.'
                                : 'Start by creating your first product idea pipeline to see it appear here.'}
                        </p>
                        {apiStatus === 'offline' ? (
                            <button
                                onClick={() => { setLoading(true); checkApiStatus(); fetchProjects(); }}
                                className="bg-blue-600 text-white px-8 py-4 rounded-2xl font-black hover:bg-blue-500 transition shadow-xl flex items-center gap-2"
                            >
                                <RotateCcw className="w-5 h-5" />
                                Retry Connection
                            </button>
                        ) : (
                            <Link href="/create">
                                <button className="bg-white text-black px-8 py-4 rounded-2xl font-black hover:bg-slate-200 transition shadow-xl">
                                    Create New Project
                                </button>
                            </Link>
                        )}
                    </div>
                )}
            </div>

            {/* Background Decorative Elements */}
            <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
                <div className="absolute top-1/4 -left-20 w-[600px] h-[600px] bg-blue-600/5 blur-[120px] rounded-full" />
                <div className="absolute bottom-1/4 -right-20 w-[600px] h-[600px] bg-purple-600/5 blur-[120px] rounded-full" />
            </div>
        </main>
    );
}
