"use client";
import Link from 'next/link';
import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
    Search, Filter, ChevronDown, MoreVertical,
    Folders, CheckCircle2, Activity, Clock,
    ArrowDown, Trash2, ExternalLink, LayoutGrid,
    Layout, Settings, History, Info, FileText
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_BASE_URL } from '@/lib/api-config';


export default function ProjectsPage() {
    const [projects, setProjects] = useState<any[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState('All Status');
    const [timeFilter, setTimeFilter] = useState('All Time');
    const [sortBy, setSortBy] = useState('Last Accessed');
    const [deletingId, setDeletingId] = useState<string | null>(null);
    const [currentView, setCurrentView] = useState('History');

    const fetchProjects = () => {
        fetch(`${API_BASE_URL}/api/projects`)
            .then(res => res.json())
            .then(data => setProjects(data))

            .catch(err => console.error(err));
    };

    useEffect(() => {
        fetchProjects();
    }, []);

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) return;

        setDeletingId(id);
        try {
            const res = await fetch(`${API_BASE_URL}/api/projects/${id}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                fetchProjects();
            } else {
                alert('Failed to delete project');
            }
        } catch (e) {
            console.error(e);
            alert('Error deleting project');
        } finally {
            setDeletingId(null);
        }
    };

    const latestProject = useMemo(() => {
        if (projects.length === 0) return null;
        return [...projects].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())[0];
    }, [projects]);

    const stats = useMemo(() => {
        const total = projects.length;
        const completed = projects.filter(p => p.status === 'COMPLETED').length;
        const active = projects.filter(p => ['ANALYSIS', 'DESIGN', 'CODING'].includes(p.status)).length;
        const successRate = total > 0 ? Math.round((completed / total) * 100) : 0;

        return {
            total,
            completed,
            active,
            successRate,
            avgTime: "38 min"
        };
    }, [projects]);

    const filteredProjects = useMemo(() => {
        return projects.filter(p => {
            const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                p.description.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesStatus = statusFilter === 'All Status' || p.status === statusFilter.toUpperCase();
            return matchesSearch && matchesStatus;
        });
    }, [projects, searchQuery, statusFilter]);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'COMPLETED': return 'text-emerald-400 bg-emerald-500/10 ring-emerald-500/20';
            case 'FAILED': return 'text-rose-400 bg-rose-500/10 ring-rose-500/20';
            case 'ANALYSIS':
            case 'DESIGN':
            case 'CODING':
            case 'PROCESSING':
            case 'NEW': return 'text-blue-400 bg-blue-500/10 ring-blue-500/20 animate-pulse';
            case 'ARCHIVED': return 'text-slate-500 bg-slate-500/10 ring-slate-500/20';
            default: return 'text-slate-400 bg-slate-500/10 ring-slate-500/20';
        }
    };

    const getProgress = (status: string) => {
        switch (status) {
            case 'COMPLETED': return 100;
            case 'CODING': return 75;
            case 'DESIGN': return 50;
            case 'ANALYSIS': return 25;
            case 'NEW': return 10;
            case 'FAILED': return 35;
            default: return 0;
        }
    };

    return (
        <main className="min-h-screen bg-[#020617] text-slate-100 font-sans selection:bg-blue-500/30 pb-20">
            {/* Navigation */}
            <nav className="border-b border-slate-800 bg-[#020617]/80 backdrop-blur-md sticky top-0 z-40">
                <div className="max-w-[1400px] mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-8">
                        <Link href="/" className="flex items-center gap-2.5">
                            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                                <Layout className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold tracking-tight text-white">Idea-to-deploy</span>
                        </Link>
                        <div className="hidden md:flex items-center gap-1">
                            {[
                                { id: 'Dashboard', icon: LayoutGrid, path: '/' },
                                { id: 'Pipeline', icon: Activity, path: latestProject ? `/project/${latestProject.id}?view=Pipeline` : '#' },
                                { id: 'Results', icon: FileText, path: latestProject ? `/project/${latestProject.id}?view=Results` : '#' },
                                { id: 'History', icon: History, path: '/projects' },
                            ].map((item) => (
                                <Link
                                    key={item.id}
                                    href={item.path}
                                    className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-all text-sm font-bold ${currentView === item.id
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
                        <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-white">
                            <Settings className="w-5 h-5" />
                        </button>
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600" />
                    </div>
                </div>
            </nav>

            <div className="max-w-[1400px] mx-auto px-6 py-10 space-y-10">
                {/* Header Section */}
                <div>
                    <h1 className="text-4xl font-black mb-2 tracking-tight text-white">Project History</h1>
                    <p className="text-slate-400 font-medium">Manage and access all your previously processed product ideas and generated development assets.</p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {[
                        { label: 'Total Projects', value: stats.total, sub: '↑ 12% vs last month', icon: Folders, color: 'blue' },
                        { label: 'Completed', value: stats.completed, sub: `${stats.successRate}% success rate`, icon: CheckCircle2, color: 'emerald' },
                        { label: 'Active Pipelines', value: stats.active, sub: 'Running now', icon: Activity, color: 'blue' },
                        { label: 'Avg Processing Time', value: stats.avgTime, sub: '5.2 hours total', icon: Clock, color: 'blue' },
                    ].map((stat, i) => (
                        <div key={i} className="bg-[#0f172a] border border-slate-800 p-6 rounded-[1.5rem] relative overflow-hidden group hover:border-slate-700 transition-all">
                            <div className="relative z-10">
                                <p className="text-slate-500 text-xs font-bold uppercase tracking-widest mb-4 flex items-center justify-between">
                                    {stat.label}
                                    <stat.icon className={`w-4 h-4 text-blue-500 group-hover:text-blue-400 transition-colors`} />
                                </p>
                                <h3 className="text-4xl font-black mb-2 text-white">{stat.value}</h3>
                                <p className={`text-xs font-semibold ${stat.color === 'emerald' ? 'text-emerald-400' : 'text-slate-500'} flex items-center gap-1`}>
                                    {stat.color === 'blue' && <span className="text-emerald-400">↗</span>}
                                    {stat.sub}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Filter & Search Bar */}
                <div className="bg-[#0f172a]/50 p-4 rounded-3xl border border-slate-800 flex flex-col md:flex-row items-center gap-4">
                    <div className="grow relative w-full md:w-auto">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Search projects by name or idea..."
                            className="w-full bg-slate-950 border border-slate-800 rounded-2xl py-3 pl-12 pr-4 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all font-medium"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <div className="flex gap-3 w-full md:w-auto">
                        {[
                            { value: statusFilter, setter: setStatusFilter, options: ['All Status', 'Completed', 'Processing', 'Failed', 'Archived'] },
                            { value: timeFilter, setter: setTimeFilter, options: ['All Time', 'Last 7 Days', 'Last 30 Days', 'Custom Range'] },
                            { value: sortBy, setter: setSortBy, options: ['Last Accessed', 'Newest First', 'Oldest First'] },
                        ].map((filter, i) => (
                            <div key={i} className="relative group min-w-[140px]">
                                <select
                                    className="appearance-none w-full bg-slate-950 border border-slate-800 rounded-2xl py-3 px-5 text-slate-300 font-bold text-xs uppercase tracking-widest hover:bg-slate-900 transition-all cursor-pointer focus:outline-none"
                                    value={filter.value}
                                    onChange={(e) => filter.setter(e.target.value)}
                                >
                                    {filter.options.map(opt => <option key={opt}>{opt}</option>)}
                                </select>
                                <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
                            </div>
                        ))}
                        <button className="flex items-center justify-center p-3.5 bg-slate-950 border border-slate-800 rounded-2xl text-slate-400 hover:text-white hover:bg-slate-900 transition-all">
                            <ArrowDown className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                {/* Projects Table */}
                <div className="overflow-hidden bg-[#0f172a]/20 border border-slate-800 rounded-[2rem] shadow-2xl">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-slate-800/80 bg-slate-900/10">
                                <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
                                    <input type="checkbox" className="w-4 h-4 rounded border-slate-800 bg-slate-950 text-blue-600 focus:ring-blue-500" />
                                </th>
                                <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Project Name</th>
                                <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Created</th>
                                <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 text-center">Status</th>
                                <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 text-center">Progress</th>
                                <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Last Accessed</th>
                                <th className="p-6 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50">
                            {filteredProjects.map((project) => (
                                <motion.tr
                                    key={project.id}
                                    layout
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="group hover:bg-slate-800/20 transition-all duration-300"
                                >
                                    <td className="p-6">
                                        <input type="checkbox" className="w-4 h-4 rounded border-slate-800 bg-slate-950 text-blue-600 focus:ring-blue-500" />
                                    </td>
                                    <td className="p-6">
                                        <Link href={`/project/${project.id}`} className="block">
                                            <div className="flex flex-col">
                                                <span className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors">{project.name}</span>
                                                <span className="text-sm text-slate-500 line-clamp-1 max-w-sm font-medium">{project.description}</span>
                                            </div>
                                        </Link>
                                    </td>
                                    <td className="p-6 whitespace-nowrap">
                                        <span className="text-sm font-bold text-slate-400">
                                            {new Date(project.createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                                        </span>
                                    </td>
                                    <td className="p-6 text-center">
                                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ring-1 ${getStatusColor(project.status)}`}>
                                            <div className={`w-1 h-1 rounded-full bg-current ${project.status === 'PROCESSING' ? 'animate-ping' : ''}`} />
                                            {project.status === 'NEW' || project.status === 'ANALYSIS' || project.status === 'DESIGN' || project.status === 'CODING' ? 'Processing' : project.status}
                                        </span>
                                    </td>
                                    <td className="p-6 w-48">
                                        <div className="flex items-center justify-center gap-4">
                                            <div className="relative w-10 h-10 flex-shrink-0">
                                                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                                                    <circle cx="18" cy="18" r="16" fill="none" className="stroke-slate-800" strokeWidth="3" />
                                                    <motion.circle
                                                        cx="18" cy="18" r="16" fill="none"
                                                        className={`stroke-${project.status === 'COMPLETED' ? 'emerald' : project.status === 'FAILED' ? 'rose' : 'blue'}-500`}
                                                        strokeWidth="3"
                                                        strokeDasharray="100 100"
                                                        initial={{ strokeDashoffset: 100 }}
                                                        animate={{ strokeDashoffset: 100 - getProgress(project.status) }}
                                                        transition={{ duration: 1, ease: "easeOut" }}
                                                    />
                                                </svg>
                                                <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white">
                                                    {getProgress(project.status)}%
                                                </span>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="p-6 whitespace-nowrap">
                                        <span className="text-sm font-bold text-slate-400">
                                            {project.updatedAt ? "2d ago" : "Yesterday"}
                                        </span>
                                    </td>
                                    <td className="p-6 text-right">
                                        <div className="flex justify-end gap-2">
                                            <Link href={`/project/${project.id}`}>
                                                <button className="p-2.5 bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-all" title="Open Project">
                                                    <ExternalLink className="w-4 h-4" />
                                                </button>
                                            </Link>
                                            <button
                                                onClick={() => handleDelete(project.id)}
                                                disabled={deletingId === project.id}
                                                className="p-2.5 bg-slate-900 border border-slate-800 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 hover:border-rose-500/20 rounded-xl transition-all"
                                                title="Delete Project"
                                            >
                                                {deletingId === project.id ? (
                                                    <div className="w-4 h-4 border-2 border-slate-500 border-t-transparent animate-spin rounded-full" />
                                                ) : (
                                                    <Trash2 className="w-4 h-4" />
                                                )}
                                            </button>
                                        </div>
                                    </td>
                                </motion.tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    );
}
