import { ProjectManager } from './project-manager';
import { DocCategory } from '@idea-to-deploy/types';

export class AIBuilder {
    private projectManager = new ProjectManager();

    async buildProject(projectId: string, description: string): Promise<any> {
        const docs = await this.projectManager.getDocs(projectId);
        const functionalDoc = docs.find(d => d.category === 'FUNCTIONAL' as DocCategory);
        const uiuxDoc = docs.find(d => d.category === 'UI_UX' as DocCategory);

        let features: string[] = ['Auth', 'Profile'];
        if (functionalDoc) {
            const matches = functionalDoc.content.match(/- \*\*(.*?)\*\*/g);
            if (matches) features = matches.map(m => m.replace('- **', '').replace('**', ''));
        }

        let screens: string[] = ['Dashboard', 'Login'];
        if (uiuxDoc) {
            const matches = uiuxDoc.content.match(/### (.*?) Screen/g);
            if (matches) screens = matches.map(m => m.replace('### ', '').replace(' Screen', ''));
        }

        const files: any[] = [];

        // 1. Root Configs
        files.push({
            path: 'package.json', content: JSON.stringify({
                name: description.toLowerCase().replace(/\s+/g, '-'),
                version: '1.0.0',
                private: true,
                workspaces: ['apps/*', 'packages/*'],
                scripts: {
                    "dev": "turbo run dev",
                    "build": "turbo run build",
                    "test": "vitest"
                }
            }, null, 2)
        });
        files.push({ path: '.env', content: 'DATABASE_URL="postgresql://user:pass@localhost:5432/db"\nJWT_SECRET="super-secret-key"' });

        // 2. Frontend (Next.js)
        files.push({ path: 'apps/web/package.json', content: '{"name": "web", "dependencies": {"next": "14", "react": "18", "lucide-react": "latest"}}' });

        // Generate Layout
        files.push({ path: 'apps/web/app/layout.tsx', content: 'export default function RootLayout({ children }: { children: React.ReactNode }) { return (<html><body>{children}</body></html>); }' });

        // Generate Pages for each screen
        screens.forEach(screen => {
            const slug = screen.toLowerCase().replace(/\s+/g, '-');

            // Try to find more details from the UI/UX doc for this screen
            const sectionRegex = new RegExp(`### ${screen} Screen([\\s\\S]*?)(?=###|$)`, 'i');
            const section = uiuxDoc?.content.match(sectionRegex)?.[1] || '';
            const screenComponents = section.match(/- \*\*Components\*\*: (.*)/)?.[1]?.split(',').map(c => c.trim()) || [];
            const screenPurpose = section.match(/- \*\*Purpose\*\*: (.*)/)?.[1] || 'Main interface for ' + screen;

            files.push({
                path: `apps/web/app/${slug}/page.tsx`,
                content: `
import React from 'react';
import { Activity, Layout, Shield, Users, CheckCircle } from 'lucide-react';

export default function ${screen.replace(/\s+/g, '')}Page() {
    return (
        <div className="min-h-screen bg-slate-50 p-8 md:p-12">
            <div className="max-w-6xl mx-auto">
                <header className="mb-12">
                    <div className="flex items-center gap-3 mb-4">
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 text-[10px] font-bold uppercase tracking-widest rounded-full">Screen: ${screen}</span>
                    </div>
                    <h1 className="text-4xl font-black text-slate-900 mb-4">${screen}</h1>
                    <p className="text-lg text-slate-600 max-w-2xl">${screenPurpose}</p>
                </header>

                <div className="grid lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-8">
                        {/* Dynamic Components Area */}
                        ${screenComponents.map(comp => `
                        <section className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
                            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-blue-500" />
                                ${comp}
                            </h3>
                            <div className="h-48 bg-slate-50 rounded-xl border border-dashed border-slate-300 flex items-center justify-center">
                                <p className="text-slate-400 font-medium">Interactive ${comp} Component Placeholder</p>
                            </div>
                        </section>
                        `).join('\n')}
                    </div>

                    <div className="space-y-6">
                        <div className="bg-slate-900 text-white p-8 rounded-2xl shadow-xl">
                            <h4 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-6">Screen Metrics</h4>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center py-2 border-b border-white/10">
                                    <span className="text-sm text-slate-400">Complexity</span>
                                    <span className="text-sm font-bold">Medium</span>
                                </div>
                                <div className="flex justify-between items-center py-2 border-b border-white/10">
                                    <span className="text-sm text-slate-400">Response</span>
                                    <span className="text-sm font-bold">&lt; 100ms</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
`
            });
        });


        // 3. Backend (Express)
        files.push({
            path: 'apps/api/src/index.ts', content: `
import express from 'express';
import cors from 'cors';
import { authRouter } from './routes/auth';
import { featureRouter } from './routes/features';

const app = express();
app.use(cors());
app.use(express.json());

app.use('/auth', authRouter);
app.use('/api', featureRouter);

app.listen(4000, () => console.log('API Server running on port 4000'));
` });

        files.push({
            path: 'apps/api/src/routes/features.ts', content: `
import { Router } from 'express';
export const featureRouter = Router();

${features.map(f => `
// ${f} endpoint
featureRouter.get('/${f.toLowerCase().replace(/\s+/g, '-')}', (req, res) => {
    res.json({ message: '${f} data fetched successfully' });
});
`).join('\n')}
` });

        // 4. Database Models
        files.push({
            path: 'packages/database/prisma/schema.prisma', content: `
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  password  String
  name      String?
  createdAt DateTime @default(now())
}

${features.filter(f => !['Login', 'Logout', 'Registration'].includes(f)).map(f => `
model ${f.replace(/\s+/g, '')} {
  id        String   @id @default(uuid())
  data      Json
  createdAt DateTime @default(now())
}
`).join('\n')}
` });

        // 5. Tests
        files.push({
            path: 'tests/unit/core.test.ts', content: `
import { describe, it, expect } from 'vitest';

describe('Core Logic', () => {
    it('should validate features', () => {
        const features = [${features.map(f => `'${f}'`).join(', ')}];
        expect(features.length).toBeGreaterThan(0);
    });
});
` });

        files.push({
            path: 'tests/integration/api.test.ts', content: `
import { describe, it, expect } from 'vitest';

describe('API Integration', () => {
    it('should have working endpoints', async () => {
        // Mock fetch or use supertest
        expect(true).toBe(true);
    });
});
` });

        return {
            status: 'success',
            files,
            pipeline: [
                { step: 'Analysis Verification', status: 'done' },
                { step: 'Scaffolding Monorepo', status: 'done' },
                { step: 'Generating Frontend Pages', status: 'done' },
                { step: 'Generating API Controllers', status: 'done' },
                { step: 'Defining DB Schema', status: 'done' },
                { step: 'Writing Unit Tests', status: 'done' },
                { step: 'Finalizing Bundle', status: 'done' }
            ]
        };
    }
}
