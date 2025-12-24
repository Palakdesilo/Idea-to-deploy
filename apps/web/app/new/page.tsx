'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';

export default function NewProject() {
    const [idea, setIdea] = useState('');
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const project = await apiClient.createProject(idea);
            // Trigger analysis immediately (or let user do it)
            await apiClient.analyze(project.id);
            router.push(\`/projects/\${project.id}\`);
    } catch (err) {
      console.error(err);
      alert('Failed to start project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-card border rounded-xl p-8 shadow-2xl">
        <h1 className="text-3xl font-bold mb-2">What are we building today?</h1>
        <p className="text-muted-foreground mb-6">Describe your idea in detail. The AI will handle the rest.</p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea 
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            className="w-full h-40 bg-background border rounded-lg p-4 focus:ring-2 focus:ring-primary outline-none resize-none"
            placeholder="e.g. A marketplace for freelance graphic designers with AI matching..."
            required
          />
          <div className="flex justify-end">
             <button 
               type="submit" 
               disabled={loading}
               className="bg-primary text-primary-foreground px-6 py-3 rounded-lg font-medium hover:opacity-90 disabled:opacity-50"
             >
               {loading ? 'Initializing Engine...' : 'Generate Platform'}
             </button>
          </div>
        </form>
      </div>
    </div>
  );
}
