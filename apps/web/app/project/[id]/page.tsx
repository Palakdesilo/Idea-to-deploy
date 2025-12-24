"use client";
import Link from 'next/link';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import {
    FileText, Eye, Download, X, Layout,
    Code, Server, ShieldCheck, ChevronRight,
    Search, Filter, Share2, RotateCcw,
    Database, Settings, Terminal, Box,
    ClipboardList, Users, ListTodo, Map,
    Activity, Shield, CheckCircle2, Clock,
    LayoutGrid, History, Plus, AlertCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

import { useEffect, useState, useMemo } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { API_BASE_URL } from '@/lib/api-config';


export default function ProjectDashboard() {
    const params = useParams();
    const router = useRouter();
    const searchParams = useSearchParams();
    const id = params.id as string;
    const [project, setProject] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    const [analyzing, setAnalyzing] = useState(false);
    const [designing, setDesigning] = useState(false);

    const [docs, setDocs] = useState<any[]>([]);
    const [visuals, setVisuals] = useState<any[]>([]);

    const [coding, setCoding] = useState(false);
    const [buildResult, setBuildResult] = useState<any>(null);
    const [activeStep, setActiveStep] = useState(1);
    const [activeTab, setActiveTab] = useState('Docs');
    const [previewDoc, setPreviewDoc] = useState<any>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [currentView, setCurrentView] = useState('Pipeline');

    const categorizedFiles = useMemo(() => {
        if (!buildResult || !buildResult.files) return { frontend: [], backend: [], tests: [] };
        const files = buildResult.files;
        return {
            frontend: files.filter((f: any) => f.path.toLowerCase().includes('web') || f.path.toLowerCase().includes('frontend') || f.path.toLowerCase().includes('ui') || f.path.toLowerCase().includes('app')),
            backend: files.filter((f: any) => f.path.toLowerCase().includes('api') || f.path.toLowerCase().includes('backend') || f.path.toLowerCase().includes('server') || f.path.toLowerCase().includes('src/index')),
            tests: files.filter((f: any) => f.path.toLowerCase().includes('test') || f.path.toLowerCase().includes('spec')),
        };
    }, [buildResult]);

    const steps = [
        { id: 1, label: 'Analysis', description: 'Requirement & Planning' },
        { id: 2, label: 'Design', description: 'UI/UX & Visuals' },
        { id: 3, label: 'Build', description: 'Code Generation' },
    ];

    const downloadZip = async () => {
        if (!buildResult) return;

        try {
            const zip = new JSZip();
            buildResult.files.forEach((file: any) => {
                zip.file(file.path, file.content);
            });

            const content = await zip.generateAsync({ type: "blob" });
            saveAs(content, `${project.name.replace(/\s+/g, '-').toLowerCase().slice(0, 30)}.zip`);
        } catch (error) {
            console.error('Download failed', error);
            alert('Download failed. Check console.');
        }
    };

    useEffect(() => {
        const view = searchParams.get('view');
        if (view) {
            setCurrentView(view);
        }
    }, [searchParams]);

    // Handle tab auto-switching based on activeStep
    useEffect(() => {
        if (activeStep === 1) setActiveTab('Docs');
        else if (activeStep === 2) setActiveTab('Designs');
        else if (activeStep === 3) setActiveTab('Frontend');
    }, [activeStep]);

    useEffect(() => {
        if (id) {
            fetchProject(true);
            fetchDocs();
            fetchVisuals();
            fetchBuild();
        }
    }, [id]);

    const fetchProject = async (isInitial = false) => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/projects/${id}`);
            if (!res.ok) throw new Error('Failed to fetch project');
            const data = await res.json();
            setProject(data);

            if (isInitial) {
                if (data.status === 'PLANNING') {
                    setActiveStep(2);
                } else if (data.status === 'DESIGNED' || data.status === 'CODING' || data.status === 'COMPLETED') {
                    setActiveStep(3);
                } else if (data.status === 'DESIGN') {
                    setActiveStep(2);
                } else {
                    setActiveStep(1);
                }

                const viewParam = searchParams.get('view');
                if (viewParam) {
                    setCurrentView(viewParam);
                } else if (data.status !== 'COMPLETED') {
                    setCurrentView('Pipeline');
                } else {
                    setCurrentView('Results');
                }
            }

            if (data.status === 'COMPLETED') {
                fetchBuild();
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const fetchDocs = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/projects/${id}/docs`);
            if (res.ok) {
                const data = await res.json();
                setDocs(data);
            }
        } catch (error) {
            console.error(error);
        }
    };

    const fetchVisuals = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/projects/${id}/visuals?t=${Date.now()}`);
            if (res.ok) {
                const data = await res.json();
                setVisuals(data);
            }
        } catch (error) {
            console.error(error);
        }
    };

    const fetchBuild = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/projects/${id}/build`);
            if (res.ok) {
                const data = await res.json();
                setBuildResult(data);
            }
        } catch (error) {
            console.error(error);
        }
    };

    const runAnalysis = async () => {
        setAnalyzing(true);
        try {
            await fetch(`${API_BASE_URL}/api/projects/${id}/analyze`, { method: 'POST' });
            await fetchProject();
            await fetchDocs();
        } catch (e) {
            console.error(e);
        } finally {
            setAnalyzing(false);
        }
    };

    const runDesign = async () => {
        setDesigning(true);
        try {
            await fetch(`${API_BASE_URL}/api/projects/${id}/design`, { method: 'POST' });
            await fetchProject();
            await fetchVisuals();
        } catch (e) {
            console.error(e);
        } finally {
            setDesigning(false);
        }
    };

    const runBuild = async () => {
        setCoding(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/projects/${id}/build`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                setBuildResult(data);
                await fetchProject();
            }
        } catch (e) {
            console.error(e);
        } finally {
            setCoding(false);
        }
    };

    const getDocIcon = (title: string) => {
        const t = title.toLowerCase();
        if (t.includes('requirement')) return <FileText className="w-6 h-6 text-blue-400" />;
        if (t.includes('planning')) return <ListTodo className="w-6 h-6 text-indigo-400" />;
        if (t.includes('architecture')) return <Box className="w-6 h-6 text-cyan-400" />;
        if (t.includes('ipmp')) return <Activity className="w-6 h-6 text-emerald-400" />;
        if (t.includes('schedule') || t.includes('cost')) return <Clock className="w-6 h-6 text-amber-400" />;
        if (t.includes('quality') || t.includes('risk')) return <ShieldCheck className="w-6 h-6 text-rose-400" />;
        if (t.includes('test') || t.includes('release')) return <RotateCcw className="w-6 h-6 text-indigo-500" />;
        return <FileText className="w-6 h-6 text-gray-400" />;
    };

    const downloadDoc = (doc: any) => {
        const blob = new Blob([doc.content], { type: 'text/markdown' });
        saveAs(blob, `${doc.title.replace(/\s+/g, '-').toLowerCase()}.md`);
    };

    const DocumentCard = ({ doc }: { doc: any }) => (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="group relative bg-[#1e293b]/40 backdrop-blur-sm border border-slate-800 rounded-2xl p-6 hover:bg-[#1e293b]/60 transition-all duration-300 flex flex-col h-full"
        >
            <div className="flex items-start justify-between mb-4">
                <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-700/50">
                    {getDocIcon(doc.title)}
                </div>
                <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{Math.ceil(doc.content.length / 1500)} pages</span>
                </div>
            </div>

            <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">{doc.title}</h3>
            <p className="text-slate-400 text-sm line-clamp-2 mb-6 flex-grow">
                {doc.content.split('\n').find((l: string) => l.length > 20 && !l.startsWith('#')) || "Detailed documentation for the project implementation."}
            </p>

            <div className="flex items-center gap-3">
                <button
                    onClick={() => setPreviewDoc(doc)}
                    className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white transition-all text-sm font-semibold"
                >
                    <Eye className="w-4 h-4" />
                    Preview
                </button>
                <button
                    onClick={() => downloadDoc(doc)}
                    className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-blue-600 text-white hover:bg-blue-500 transition-all text-sm font-semibold shadow-lg shadow-blue-500/20"
                >
                    <Download className="w-4 h-4" />
                    Download
                </button>
            </div>
        </motion.div>
    );

    const DocumentPreviewModal = () => (
        <AnimatePresence>
            {previewDoc && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setPreviewDoc(null)}
                        className="absolute inset-0 bg-slate-950/80 backdrop-blur-md"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="relative w-full max-w-4xl max-h-[90vh] bg-[#0f172a] border border-slate-800 rounded-3xl overflow-hidden shadow-2xl flex flex-col"
                    >
                        <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-900/50">
                            <div className="flex items-center gap-4">
                                <div className="p-2.5 bg-blue-500/10 rounded-xl border border-blue-500/20">
                                    {getDocIcon(previewDoc.title)}
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold text-white">{previewDoc.title}</h2>
                                    <p className="text-sm text-slate-400">Project: {project.name}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={() => downloadDoc(previewDoc)}
                                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all font-semibold shadow-lg shadow-blue-500/20"
                                >
                                    <Download className="w-4 h-4" />
                                    Download
                                </button>
                                <button
                                    onClick={() => setPreviewDoc(null)}
                                    className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
                                >
                                    <X className="w-6 h-6" />
                                </button>
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar bg-[linear-gradient(to_bottom,_transparent,_var(--tw-gradient-from)_20%),_radial-gradient(ellipse_at_top,_var(--tw-gradient-from),_transparent)] from-slate-900 via-slate-950 to-slate-950">
                            <article className="prose prose-invert prose-blue max-w-none">
                                <ReactMarkdown
                                    components={{
                                        h1: ({ node, ...props }) => <h1 className="text-3xl font-extrabold mb-8 bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent" {...props} />,
                                        h2: ({ node, ...props }) => <h2 className="text-2xl font-bold mt-12 mb-6 border-b border-slate-800 pb-2 text-blue-400" {...props} />,
                                        h3: ({ node, ...props }) => <h3 className="text-xl font-semibold mt-8 mb-4 text-slate-200" {...props} />,
                                        p: ({ node, ...props }) => <p className="text-slate-300 leading-relaxed mb-6" {...props} />,
                                        ul: ({ node, ...props }) => <ul className="space-y-3 mb-6" {...props} />,
                                        li: ({ node, ...props }) => <li className="flex items-start gap-3 text-slate-300" {...props} />,
                                        code: ({ node, ...props }) => <code className="bg-slate-800 px-1.5 py-0.5 rounded text-blue-300 font-mono text-sm" {...props} />,
                                        strong: ({ node, ...props }) => <strong className="text-blue-200 font-bold" {...props} />,
                                    }}
                                >
                                    {previewDoc.content}
                                </ReactMarkdown>
                            </article>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );

    if (loading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Loading...</div>;
    if (!project) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Project not found</div>;

    const isCompleted = project.status === 'COMPLETED';

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
                                { id: 'Dashboard', icon: LayoutGrid, path: '/' },
                                { id: 'Pipeline', icon: Activity, path: `/project/${id}?view=Pipeline` },
                                { id: 'Results', icon: FileText, path: `/project/${id}?view=Results` },
                                { id: 'History', icon: History, path: '/projects' },
                            ].map((item) => (
                                <Link
                                    key={item.id}
                                    href={item.path}
                                    className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-all text-sm font-bold ${currentView === item.id
                                        ? 'bg-blue-600/10 text-blue-400'
                                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                                        }`}
                                >
                                    <item.icon className="w-4 h-4" />
                                    {item.id}
                                </Link>
                            ))}
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
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

            <div className="max-w-[1400px] mx-auto px-10 py-10">
                {/* Unified Project Header */}
                <div className="mb-8">
                    <Link href="/" className="text-slate-400 hover:text-white flex items-center gap-2 transition w-fit group">
                        <ChevronRight className="w-5 h-5 rotate-180 group-hover:-translate-x-1 transition-transform" />
                        <span className="hover:underline">Back to Projects</span>
                    </Link>
                </div>

                <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 bg-[#0f172a] p-10 rounded-[2.5rem] border border-slate-800 shadow-2xl relative overflow-hidden group mb-10">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/5 blur-[120px] rounded-full -mr-48 -mt-48 transition-all group-hover:bg-blue-600/10" />
                    <div className="relative z-10 flex-1">
                        <div className="flex items-center gap-3 mb-6">
                            <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] ring-1 ${isCompleted ? 'bg-emerald-500/10 text-emerald-400 ring-emerald-500/20' : 'bg-blue-500/10 text-blue-400 ring-blue-500/20 animate-pulse'}`}>
                                {isCompleted ? 'Pipeline Completed' : 'Active Pipeline'}
                            </span>
                            <div className="h-[1px] w-8 bg-slate-800" />
                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em]">Created on {new Date(project.createdAt).toLocaleDateString()}</span>
                        </div>
                        <h1 className="text-5xl font-black mb-4 tracking-tight">{project.name}</h1>
                        <p className="text-slate-400 text-lg max-w-3xl leading-relaxed">{project.description}</p>
                    </div>

                    {isCompleted && (
                        <div className="flex items-center gap-3 relative z-10 w-full md:w-auto">
                            <button
                                onClick={downloadZip}
                                className="flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-4 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded-2xl transition-all font-bold text-slate-200"
                            >
                                <Download className="w-5 h-5" />
                                Download All
                            </button>
                            <button className="flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-2xl transition-all font-bold shadow-lg shadow-blue-500/25">
                                <Share2 className="w-5 h-5" />
                                Export
                            </button>
                        </div>
                    )}
                </div>

                {/* Sub-navigation Tabs */}
                <div className="flex items-center gap-2 border-b border-slate-800/60 mb-10 overflow-x-auto scrollbar-hide">
                    {[
                        { id: 'Pipeline', label: 'Development Pipeline', icon: Activity },
                        { id: 'Results', label: 'Output Assets', icon: Box, hidden: !isCompleted && docs.length === 0 },
                    ].filter(tab => !tab.hidden).map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setCurrentView(tab.id)}
                            className={`group relative flex items-center gap-3 px-8 py-4 transition-all font-bold text-sm whitespace-nowrap ${currentView === tab.id
                                ? 'text-blue-400'
                                : 'text-slate-500 hover:text-slate-300'
                                }`}
                        >
                            <tab.icon className={`w-4 h-4 ${currentView === tab.id ? 'text-blue-400' : 'text-slate-500 hover:text-slate-300'}`} />
                            {tab.label}
                            {currentView === tab.id && (
                                <motion.div layoutId="projectTab" className="absolute bottom-[-1px] left-0 right-0 h-0.5 bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
                            )}
                        </button>
                    ))}
                </div>

                <AnimatePresence mode="wait">
                    {currentView === 'Pipeline' ? (
                        <motion.div
                            key="pipeline"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.2 }}
                        >
                            {/* Pipeline Content */}
                            <div className="max-w-4xl mx-auto mb-20 relative px-12">
                                <div className="absolute top-5 left-12 right-12 h-[2px] bg-slate-800 z-0">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: project.status === 'COMPLETED' ? '100%' : project.status === 'CODING' ? '66%' : project.status === 'PLANNING' ? '33%' : '0%' }}
                                        className="h-full bg-blue-600 shadow-[0_0_10px_rgba(37,99,235,0.5)]"
                                    />
                                </div>
                                <div className="flex justify-between relative z-10">
                                    {steps.map((step) => {
                                        const stepCompleted = (step.id === 1 && (['PLANNING', 'DESIGN', 'CODING', 'COMPLETED', 'DESIGNED'].includes(project.status))) ||
                                            (step.id === 2 && (['CODING', 'COMPLETED', 'DESIGNED'].includes(project.status))) ||
                                            (step.id === 3 && project.status === 'COMPLETED');
                                        const isActive = activeStep === step.id;

                                        return (
                                            <button
                                                key={step.id}
                                                onClick={() => setActiveStep(step.id)}
                                                className={`flex flex-col items-center group ${isActive ? 'cursor-default' : 'cursor-pointer'}`}
                                            >
                                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center border-2 transition-all duration-500 ${stepCompleted ? 'bg-emerald-500 border-emerald-500 text-white' :
                                                    isActive ? 'bg-blue-600 border-blue-600 text-white scale-110 shadow-lg shadow-blue-500/40' :
                                                        'bg-slate-900 border-slate-700 text-slate-500 group-hover:border-slate-500'
                                                    }`}>
                                                    {stepCompleted ? <CheckCircle2 className="w-6 h-6" /> : <span className="text-sm font-bold">{step.id}</span>}
                                                </div>
                                                <div className="mt-4 text-center">
                                                    <p className={`text-xs font-bold uppercase tracking-widest ${isActive ? 'text-white' : 'text-slate-500'}`}>{step.label}</p>
                                                </div>
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>

                            <div className="max-w-5xl mx-auto min-h-[400px]">
                                {activeStep === 1 && (
                                    <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="space-y-8">
                                        <div className={`p-10 rounded-3xl border ${project.status === 'ANALYSIS' ? 'border-blue-500/50 bg-blue-500/5' : 'border-slate-800 bg-slate-900/40'} shadow-2xl backdrop-blur-sm`}>
                                            <h2 className="text-2xl font-bold mb-8 flex items-center gap-4">
                                                <div className="p-3 bg-blue-600 rounded-xl flex items-center justify-center">
                                                    <Search className="w-6 h-6 text-white" />
                                                </div>
                                                Analysis Phase
                                            </h2>
                                            <div className="grid md:grid-cols-2 gap-10">
                                                <div className="space-y-6">
                                                    <p className="text-slate-400 leading-relaxed text-lg">
                                                        We analyze your product idea and generate a detailed implementation plan, database schema, and API documentation.
                                                    </p>
                                                    <div className="bg-slate-950/50 p-6 rounded-2xl border border-slate-800/50">
                                                        <h4 className="text-sm font-bold mb-4 text-slate-300 uppercase tracking-widest flex items-center gap-2">
                                                            <Box className="w-4 h-4 text-blue-400" />
                                                            Key Deliverables
                                                        </h4>
                                                        <ul className="text-sm text-slate-400 space-y-3">
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" />Technical Requirements</li>
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" />System Architecture</li>
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" />Database Schema Design</li>
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" />API Specifications</li>
                                                        </ul>
                                                    </div>
                                                </div>
                                                <div className="flex flex-col justify-center">
                                                    {project.status === 'NEW' || project.status === 'ANALYSIS' ? (
                                                        <button
                                                            onClick={runAnalysis}
                                                            disabled={analyzing}
                                                            className="w-full py-6 bg-white text-black font-extrabold rounded-2xl hover:bg-slate-200 disabled:opacity-50 transition-all flex items-center justify-center gap-3 text-lg shadow-xl"
                                                        >
                                                            {analyzing ? (
                                                                <>
                                                                    <RotateCcw className="w-6 h-6 animate-spin" />
                                                                    Analyzing Your Idea...
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <Terminal className="w-6 h-6" />
                                                                    Start Analysis
                                                                </>
                                                            )}
                                                        </button>
                                                    ) : (
                                                        <div className="space-y-4">
                                                            <div className="flex items-center gap-3 text-emerald-400 font-bold justify-center py-6 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 text-lg">
                                                                <CheckCircle2 className="w-6 h-6" /> Analysis Completed
                                                            </div>
                                                            <button
                                                                onClick={() => setActiveStep(2)}
                                                                className="w-full py-6 bg-blue-600 text-white font-extrabold rounded-2xl hover:bg-blue-700 transition-all flex items-center justify-center gap-3 text-lg group shadow-xl shadow-blue-500/20"
                                                            >
                                                                Proceed to Design
                                                                <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                                                            </button>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}

                                {activeStep === 2 && (
                                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-8">
                                        <div className={`p-10 rounded-3xl border ${project.status === 'DESIGN' ? 'border-purple-500/50 bg-purple-500/5' : 'border-slate-800 bg-slate-900/40'} shadow-2xl backdrop-blur-sm`}>
                                            <h2 className="text-2xl font-bold mb-8 flex items-center gap-4">
                                                <div className="p-3 bg-purple-600 rounded-xl flex items-center justify-center">
                                                    <Layout className="w-6 h-6 text-white" />
                                                </div>
                                                Design Phase
                                            </h2>
                                            <div className="grid md:grid-cols-2 gap-10">
                                                <div className="space-y-6">
                                                    <p className="text-slate-400 leading-relaxed text-lg">
                                                        Our AI designer creates a visual design system, UI components, and high-fidelity mockups.
                                                    </p>
                                                    <div className="bg-slate-950/50 p-6 rounded-2xl border border-slate-800/50">
                                                        <h4 className="text-sm font-bold mb-4 text-slate-300 uppercase tracking-widest flex items-center gap-2">
                                                            <Box className="w-4 h-4 text-purple-400" />
                                                            Design Assets
                                                        </h4>
                                                        <ul className="text-sm text-slate-400 space-y-3">
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-purple-500" />Design Tokens & Palette</li>
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-purple-500" />UI Component Library</li>
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-purple-500" />Page Mockups & Layouts</li>
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-purple-500" />UX User Flows</li>
                                                        </ul>
                                                    </div>
                                                </div>
                                                <div className="flex flex-col justify-center">
                                                    {project.status === 'PLANNING' || project.status === 'DESIGN' || project.status === 'DESIGNED' ? (
                                                        <button
                                                            onClick={runDesign}
                                                            disabled={designing}
                                                            className="w-full py-6 bg-purple-600 text-white font-extrabold rounded-2xl hover:bg-purple-700 disabled:opacity-50 transition-all flex items-center justify-center gap-3 text-lg shadow-xl shadow-purple-500/20"
                                                        >
                                                            {designing ? (
                                                                <>
                                                                    <RotateCcw className="w-6 h-6 animate-spin" />
                                                                    Generating Visuals...
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <Layout className="w-6 h-6" />
                                                                    Generate Designs
                                                                </>
                                                            )}
                                                        </button>
                                                    ) : (project.status === 'DESIGNED' || project.status === 'CODING' || project.status === 'COMPLETED') ? (
                                                        <div className="space-y-4">
                                                            <div className="flex items-center gap-3 text-emerald-400 font-bold justify-center py-6 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 text-lg">
                                                                <CheckCircle2 className="w-6 h-6" /> Design Completed
                                                            </div>
                                                            <button
                                                                onClick={() => setActiveStep(3)}
                                                                className="w-full py-6 bg-purple-600 text-white font-extrabold rounded-2xl hover:bg-purple-700 transition-all flex items-center justify-center gap-3 text-lg group shadow-xl shadow-purple-500/20"
                                                            >
                                                                Proceed to Build
                                                                <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                                                            </button>
                                                        </div>
                                                    ) : (
                                                        <button disabled className="w-full py-6 bg-slate-800 text-slate-500 font-extrabold rounded-2xl opacity-50 cursor-not-allowed text-lg">
                                                            Complete Analysis First
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}

                                {activeStep === 3 && (
                                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
                                        <div className={`p-10 rounded-3xl border ${project.status === 'CODING' ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-slate-800 bg-slate-900/40'} shadow-2xl backdrop-blur-sm`}>
                                            <h2 className="text-2xl font-bold mb-8 flex items-center gap-4">
                                                <div className="p-3 bg-emerald-600 rounded-xl flex items-center justify-center">
                                                    <Code className="w-6 h-6 text-white" />
                                                </div>
                                                Build Phase
                                            </h2>
                                            <div className="grid md:grid-cols-2 gap-10">
                                                <div className="space-y-6">
                                                    <p className="text-slate-400 leading-relaxed text-lg">
                                                        We scaffold the entire codebase, including frontend pages, backend APIs, and configurations.
                                                    </p>
                                                    <div className="bg-slate-950/50 p-6 rounded-2xl border border-slate-800/50">
                                                        <h4 className="text-sm font-bold mb-4 text-slate-300 uppercase tracking-widest flex items-center gap-2">
                                                            <Box className="w-4 h-4 text-emerald-400" />
                                                            Final Outputs
                                                        </h4>
                                                        <ul className="text-sm text-slate-400 space-y-3">
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />Full-stack Next.js App</li>
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />API Implementations</li>
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />Database Migrations</li>
                                                            <li className="flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />Production Cloud Config</li>
                                                        </ul>
                                                    </div>
                                                </div>
                                                <div className="flex flex-col justify-center">
                                                    {project.status === 'DESIGNED' || project.status === 'CODING' ? (
                                                        <button
                                                            onClick={runBuild}
                                                            disabled={coding}
                                                            className="w-full py-6 bg-emerald-600 text-white font-extrabold rounded-2xl hover:bg-emerald-700 disabled:opacity-50 transition-all flex items-center justify-center gap-3 text-lg shadow-xl shadow-emerald-500/20"
                                                        >
                                                            {coding ? (
                                                                <>
                                                                    <RotateCcw className="w-6 h-6 animate-spin" />
                                                                    Building Codebase...
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <Code className="w-6 h-6" />
                                                                    Generate Codebase
                                                                </>
                                                            )}
                                                        </button>
                                                    ) : project.status === 'COMPLETED' ? (
                                                        <div className="space-y-4">
                                                            <div className="flex items-center gap-3 text-emerald-400 font-bold justify-center py-6 bg-emerald-500/10 rounded-2xl border border-emerald-500/20 text-lg">
                                                                <CheckCircle2 className="w-6 h-6" /> Build Completed
                                                            </div>
                                                            <button
                                                                onClick={() => setCurrentView('Results')}
                                                                className="w-full py-6 bg-white text-black font-extrabold rounded-2xl hover:bg-slate-200 transition-all flex items-center justify-center gap-3 text-lg shadow-xl"
                                                            >
                                                                View Result Assets
                                                                <ChevronRight className="w-6 h-6" />
                                                            </button>
                                                        </div>
                                                    ) : (
                                                        <button disabled className="w-full py-6 bg-slate-800 text-slate-500 font-extrabold rounded-2xl opacity-50 cursor-not-allowed text-lg">
                                                            Complete Design Phase First
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div
                            key="results"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.2 }}
                            className="space-y-10"
                        >
                            {/* Results Hub Content */}
                            <div className="flex items-center justify-between border-b border-slate-800/60 pb-1">
                                <div className="flex items-center gap-2">
                                    {[
                                        { id: 'Docs', count: docs.length, icon: FileText, phase: 1 },
                                        { id: 'Designs', count: visuals.length, icon: Layout, phase: 2 },
                                        { id: 'Frontend', count: categorizedFiles.frontend.length, icon: Code, phase: 3 },
                                        { id: 'Backend', count: categorizedFiles.backend.length, icon: Server, phase: 3 },
                                        { id: 'Tests', count: categorizedFiles.tests.length, icon: ShieldCheck, phase: 3 },
                                    ].filter(tab => tab.phase === activeStep).map((tab) => (
                                        <button
                                            key={tab.id}
                                            onClick={() => setActiveTab(tab.id)}
                                            className={`group relative flex items-center gap-3 px-6 py-4 rounded-t-2xl transition-all font-bold text-sm ${activeTab === tab.id
                                                ? 'text-blue-400'
                                                : 'text-slate-500 hover:text-slate-300'
                                                }`}
                                        >
                                            <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? 'text-blue-400' : 'text-slate-500'}`} />
                                            {tab.id}
                                            <span className={`px-2 py-0.5 rounded-lg text-[10px] ${activeTab === tab.id ? 'bg-blue-500 text-white' : 'bg-slate-800 text-slate-500 group-hover:bg-slate-700'
                                                }`}>
                                                {tab.count}
                                            </span>
                                            {activeTab === tab.id && (
                                                <motion.div layoutId="activeArtifactTab" className="absolute bottom-[-1px] left-0 right-0 h-0.5 bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
                                            )}
                                        </button>
                                    ))}
                                </div>
                                <div className="flex items-center gap-3 px-4 py-2 bg-slate-900/50 rounded-xl border border-slate-800">
                                    <Search className="w-4 h-4 text-slate-500" />
                                    <input
                                        type="text"
                                        placeholder="Search artifacts..."
                                        className="bg-transparent border-none outline-none text-xs text-slate-300 w-48 placeholder:text-slate-600"
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                    />
                                </div>
                            </div>

                            <div className="min-h-[500px]">
                                {activeTab === 'Docs' && (
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {docs.filter(doc => doc.title.toLowerCase().includes(searchQuery.toLowerCase())).map((doc) => (
                                            <DocumentCard key={doc.id} doc={doc} />
                                        ))}
                                        {docs.length === 0 && (
                                            <div className="col-span-full flex flex-col items-center justify-center py-20 bg-slate-900/40 rounded-[2rem] border border-dashed border-slate-800">
                                                <FileText className="w-16 h-16 text-slate-700 mb-4" />
                                                <p className="text-slate-500 font-medium">No documents generated yet</p>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeTab === 'Designs' && (
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                        {visuals.map((visual: any) => (
                                            <motion.div
                                                key={visual.id}
                                                initial={{ opacity: 0, scale: 0.98 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                className="group relative overflow-hidden rounded-[2.5rem] border border-slate-800 bg-[#0f172a] hover:border-blue-500/50 transition-all duration-500 shadow-xl flex flex-col"
                                            >
                                                <div className="aspect-[16/10] w-full overflow-hidden relative">
                                                    <img src={visual.imageUrl} alt={visual.screenName} className="h-full w-full object-cover transition-transform duration-1000 group-hover:scale-105" />
                                                    <div className="absolute inset-0 bg-gradient-to-t from-[#0f172a] via-[#0f172a]/20 to-transparent" />
                                                    <div className="absolute bottom-8 left-8 right-8">
                                                        <div className="flex items-center gap-3 mb-3">
                                                            <span className="px-3 py-1 bg-blue-600 text-[10px] font-black uppercase tracking-widest rounded-lg shadow-lg shadow-blue-600/20">Design Ready</span>
                                                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{visual.roles?.join(', ') || 'All Users'}</span>
                                                        </div>
                                                        <h3 className="text-3xl font-black text-white tracking-tight">{visual.screenName}</h3>
                                                    </div>
                                                </div>
                                                <div className="p-8 space-y-8 flex-1">
                                                    <div>
                                                        <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-3 flex items-center gap-2">
                                                            <Activity className="w-3.5 h-3.5 text-blue-500" />
                                                            Purpose & Context
                                                        </h4>
                                                        <p className="text-slate-300 text-sm leading-relaxed">{visual.purpose || visual.description}</p>
                                                    </div>

                                                    <div className="grid grid-cols-2 gap-8">
                                                        <div>
                                                            <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-3">Components</h4>
                                                            <div className="flex flex-wrap gap-2">
                                                                {visual.components?.map((c: string, i: number) => (
                                                                    <span key={i} className="text-[10px] px-2 py-1 bg-slate-900 border border-slate-800 text-slate-400 rounded-md">{c}</span>
                                                                )) || <span className="text-[10px] text-slate-600 italic text-xs">Standard UI Elements</span>}
                                                            </div>
                                                        </div>
                                                        <div>
                                                            <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-3">States</h4>
                                                            <div className="flex flex-wrap gap-2">
                                                                {visual.states?.map((s: string, i: number) => (
                                                                    <span key={i} className="text-[10px] px-2 py-1 bg-slate-900 border border-slate-800 text-slate-400 rounded-md">{s}</span>
                                                                )) || <span className="text-[10px] text-slate-600 italic text-xs">Dynamic UI States</span>}
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div className="pt-6 border-t border-slate-800/60 flex items-center justify-between">
                                                        <div className="flex items-center gap-4 text-xs font-bold text-slate-500">
                                                            <div className="flex items-center gap-1.5 hover:text-blue-400 cursor-help transition-colors">
                                                                <Users className="w-3.5 h-3.5" />
                                                                <span>{visual.roles?.length || 1} Roles</span>
                                                            </div>
                                                            <div className="flex items-center gap-1.5 hover:text-blue-400 cursor-help transition-colors">
                                                                <ListTodo className="w-3.5 h-3.5" />
                                                                <span>{visual.interactions?.length || 0} Interactions</span>
                                                            </div>
                                                        </div>
                                                        <button
                                                            onClick={() => {
                                                                const link = document.createElement('a');
                                                                link.href = visual.imageUrl;
                                                                link.download = `${visual.screenName.toLowerCase()}-design.png`;
                                                                link.click();
                                                            }}
                                                            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl transition-all text-xs font-bold border border-slate-700"
                                                        >
                                                            <Download className="w-4 h-4" />
                                                            Full Mockup
                                                        </button>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>
                                )}


                                {['Frontend', 'Backend', 'Tests'].includes(activeTab) && (
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {(activeTab === 'Frontend' ? categorizedFiles.frontend :
                                            activeTab === 'Backend' ? categorizedFiles.backend :
                                                categorizedFiles.tests).map((file: any, idx: number) => (
                                                    <motion.div
                                                        key={idx}
                                                        initial={{ opacity: 0, y: 10 }}
                                                        animate={{ opacity: 1, y: 0 }}
                                                        className="bg-[#1e293b]/40 backdrop-blur-sm border border-slate-800 rounded-2xl p-6 hover:bg-[#1e293b]/60 transition-all group"
                                                    >
                                                        <div className="flex items-start gap-4">
                                                            <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-700/50">
                                                                <Code className="w-5 h-5 text-blue-400" />
                                                            </div>
                                                            <div className="flex-1 min-w-0">
                                                                <h4 className="text-sm font-bold text-white mb-1 truncate">{file.path.split('/').pop()}</h4>
                                                                <p className="text-[10px] text-slate-500 font-mono truncate">{file.path}</p>
                                                            </div>
                                                        </div>
                                                        <div className="mt-6 flex justify-between items-center">
                                                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                                                                {file.content.length > 1024 ? `${(file.content.length / 1024).toFixed(1)} KB` : `${file.content.length} B`}
                                                            </span>
                                                            <button
                                                                onClick={() => {
                                                                    const blob = new Blob([file.content], { type: 'text/plain' });
                                                                    saveAs(blob, file.path.split('/').pop() || 'file.txt');
                                                                }}
                                                                className="p-2 hover:bg-blue-600/10 rounded-lg text-slate-400 hover:text-blue-400 transition-colors"
                                                            >
                                                                <Download className="w-4 h-4" />
                                                            </button>
                                                        </div>
                                                    </motion.div>
                                                ))}
                                        {(activeTab === 'Frontend' ? categorizedFiles.frontend.length :
                                            activeTab === 'Backend' ? categorizedFiles.backend.length :
                                                categorizedFiles.tests.length) === 0 && (
                                                <div className="col-span-full flex flex-col items-center justify-center py-32 bg-slate-900/40 rounded-[2.5rem] border border-dashed border-slate-800">
                                                    <Code className="w-20 h-20 text-slate-800 mb-6" />
                                                    <h3 className="text-2xl font-bold text-slate-300 mb-2">{activeTab} Files</h3>
                                                    <p className="text-slate-500 max-w-md text-center">
                                                        No {activeTab.toLowerCase()} files were generated for this project.
                                                    </p>
                                                </div>
                                            )}
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <DocumentPreviewModal />

            <style jsx global>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 8px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(148, 163, 184, 0.1);
                    border-radius: 10px;
                    border: 2px solid transparent;
                    background-clip: padding-box;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: rgba(148, 163, 184, 0.2);
                    background-clip: padding-box;
                }
            `}</style>
        </main>
    );
}
