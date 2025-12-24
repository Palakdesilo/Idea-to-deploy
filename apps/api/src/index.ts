import express, { Request, Response } from 'express';
import cors from 'cors';
import { ProjectManager, AIAnalyst, AIDesigner, AIBuilder } from '@idea-to-deploy/engine';
import { Project, GeneratedDoc, UIAsset } from '@idea-to-deploy/types';
import { randomUUID } from 'crypto';

const app = express();
const port = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

const projectManager = new ProjectManager();
const aiAnalyst = new AIAnalyst();
const aiDesigner = new AIDesigner();
const aiBuilder = new AIBuilder();

console.log("==========================================");
console.log("API SERVER V3: UI/UX ENGINE RELOADED");
console.log("==========================================");

app.get('/health', (req: Request, res: Response) => {
    res.json({ status: 'ok' });
});

// Create Project
app.post('/api/projects', async (req: Request, res: Response) => {
    try {
        const { idea } = req.body;
        if (!idea) return res.status(400).json({ error: 'Idea is required' });

        // Create Metadata
        const project = await projectManager.createProject(
            idea.substring(0, 50) + (idea.length > 50 ? '...' : ''),
            idea
        );

        res.json(project);

        // Background Trigger: Start Analysis logic could go here or separate endpoint
    } catch (err: any) { // Type 'any' used to ensure access to message
        res.status(500).json({ error: err.message });
    }
});

app.get('/api/projects', async (req: Request, res: Response) => {
    const projects = await projectManager.getAllProjects();
    res.json(projects);
});

app.get('/api/projects/:id', async (req: Request, res: Response) => {
    try {
        const project = await projectManager.getProject(req.params.id);
        if (!project) return res.status(404).json({ error: 'Not found' });
        res.json(project);
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// Delete Project
app.delete('/api/projects/:id', async (req: Request, res: Response) => {
    try {
        await projectManager.deleteProject(req.params.id);
        res.json({ success: true });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// Get Project Docs
app.get('/api/projects/:id/docs', async (req: Request, res: Response) => {
    try {
        const docs = await projectManager.getDocs(req.params.id);
        res.json(docs);
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// Trigger Analysis Phase
app.post('/api/projects/:id/analyze', async (req: Request, res: Response) => {
    try {
        const project = await projectManager.getProject(req.params.id);
        if (!project) return res.status(404).json({ error: 'Project not found' });

        // Update status
        await projectManager.updateProjectStatus(project.id, 'ANALYSIS');

        console.log(`Starting analysis with AIAnalyst Version: ${AIAnalyst.VERSION}`);

        // Run Analysis
        const docs = await aiAnalyst.analyzeIdea(project.description);

        // Save Docs
        const savedDocs = [];
        const categoryTitles: Record<string, string> = {
            'REQUIREMENTS': 'Requirement Document',
            'PLANNING': 'Project Planning Document',
            'ARCHITECTURE': 'Technical Architecture & Delivery Plan',
            'IPMP': 'Integrated Project Management Plan (IPMP)',
            'SCHEDULE_COST': 'Schedule & Cost Plan',
            'QUALITY_RISK': 'Quality, Risk & Procurement Plan',
            'TESTING_RELEASE': 'Testing & Release Plan',
            'UI_UX': 'UI/UX Design Specification'
        };

        for (const [category, content] of docs.entries()) {
            console.log(`Generating and saving doc for category: ${category}`);
            const title = categoryTitles[category] || `${category} Document`;
            const saved = await projectManager.saveDoc(
                project.id,
                category as any,
                title,
                content
            );
            savedDocs.push(saved);
        }

        await projectManager.updateProjectStatus(project.id, 'PLANNING');

        res.json({ success: true, docs: savedDocs });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// Trigger Design Phase (Visuals)
app.post('/api/projects/:id/design', async (req: Request, res: Response) => {
    try {
        const project = await projectManager.getProject(req.params.id);
        if (!project) return res.status(404).json({ error: 'Project not found' });

        // DIRECT ENGINE OVERRIDE TO FIX LINKING ISSUES
        const fs = require('fs-extra');
        const visualsFile = `data/artifacts/${project.id}/visuals.json`;
        if (fs.existsSync(visualsFile)) await fs.remove(visualsFile);

        const docs = await projectManager.getDocs(project.id);
        let uiuxDoc = docs.find(d => (d.category as any) === 'UI_UX');

        // Check for legacy or missing doc
        if (!uiuxDoc || !uiuxDoc.content.includes('### ')) {
            console.log('[DEBUG] Legacy UI/UX Doc detected. Regenerating...');
            const generatedDocs = await aiAnalyst.analyzeIdea(project.description);
            const uiuxContent = generatedDocs.get('UI_UX' as any);
            if (uiuxContent) {
                uiuxDoc = await projectManager.saveDoc(project.id, 'UI_UX' as any, 'UI/UX Design Specification', uiuxContent);
            }
        }

        const desc = project.description.toLowerCase();
        let cat = 'business-app';
        if (desc.includes('ecommerce') || desc.includes('shop')) cat = 'ecommerce';
        else if (desc.includes('social')) cat = 'social-media';

        const mockups: Record<string, string[]> = {
            'ecommerce': [
                'https://images.unsplash.com/photo-1557821552-17105176677c', 'https://images.unsplash.com/photo-1472851294608-062f824d29cc',
                'https://images.unsplash.com/photo-1523275335684-37898b6baf30', 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d',
                'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4'
            ],
            'social-media': [
                'https://images.unsplash.com/photo-1611162617474-5b21e879e113', 'https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0',
                'https://images.unsplash.com/photo-1611605851314-72663f9a11d4', 'https://images.unsplash.com/photo-1611606063065-ee7946f0787a',
                'https://images.unsplash.com/photo-1611162618071-b39a2ec055fb'
            ],
            'business-app': [
                'https://images.unsplash.com/photo-1551288049-bebda4e38f71', 'https://images.unsplash.com/photo-1460925895917-afdab827c52f',
                'https://images.unsplash.com/photo-1542744094-24638eff586b', 'https://images.unsplash.com/photo-1551434678-e076c223a692',
                'https://images.unsplash.com/photo-1531403009284-440f080d1e12'
            ]
        };

        const currentMockups = mockups[cat] || mockups['business-app'];
        const visuals: UIAsset[] = [];

        if (uiuxDoc) {
            const screens = uiuxDoc.content.split('### ').slice(1);
            screens.forEach((section, i) => {
                const screenName = section.split('\n')[0].trim();
                const img = currentMockups[i % currentMockups.length];
                visuals.push({
                    id: randomUUID(),
                    projectId: project.id,
                    screenName,
                    description: `Interface for ${screenName}`,
                    imageUrl: `${img}?q=80&w=1200&auto=format&fit=crop`,
                    promptUsed: `Professional UI Mockup: ${screenName}`,
                    purpose: section.match(/- \*\*Purpose\*\*: (.*)/)?.[1] || '',
                    roles: section.match(/- \*\*Roles\*\*: (.*)/)?.[1]?.split(',') || [],
                    components: section.match(/- \*\*Components\*\*: (.*)/)?.[1]?.split(',') || [],
                    interactions: section.match(/- \*\*Interactions\*\*: (.*)/)?.[1]?.split(',') || [],
                    states: section.match(/- \*\*States\*\*: (.*)/)?.[1]?.split(',') || []
                } as any);
            });
        }

        if (visuals.length === 0) {
            visuals.push({
                id: randomUUID(),
                projectId: project.id,
                screenName: 'Dashboard',
                description: 'Project Overview',
                imageUrl: `${currentMockups[0]}?q=80&w=1200&auto=format&fit=crop`,
                promptUsed: 'Dashboard Mockup'
            });
        }

        // Save persist
        await projectManager.saveVisuals(project.id, visuals);
        await projectManager.updateProjectStatus(project.id, 'DESIGNED' as any);

        res.json({ success: true, visuals });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// Get Visuals
app.get('/api/projects/:id/visuals', async (req: Request, res: Response) => {
    try {
        const visuals = await projectManager.getVisuals(req.params.id);
        res.json(visuals);
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// Trigger Build Phase
app.post('/api/projects/:id/build', async (req: Request, res: Response) => {
    try {
        const project = await projectManager.getProject(req.params.id);
        if (!project) return res.status(404).json({ error: 'Project not found' });

        await projectManager.updateProjectStatus(project.id, 'CODING');

        const buildResult = await aiBuilder.buildProject(project.id, project.description);
        await projectManager.saveBuildResult(project.id, buildResult);

        await projectManager.updateProjectStatus(project.id, 'COMPLETED');

        res.json(buildResult);
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

app.get('/api/projects/:id/build', async (req: Request, res: Response) => {
    try {
        let buildResult = await projectManager.getBuildResult(req.params.id);

        // Fallback for older projects: if completed but result missing, generate it
        if (!buildResult) {
            const project = await projectManager.getProject(req.params.id);
            if (project && project.status === 'COMPLETED') {
                buildResult = await aiBuilder.buildProject(project.id, project.description);
                await projectManager.saveBuildResult(project.id, buildResult);
            }
        }

        res.json(buildResult);
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(port, () => {
    console.log(`API Server running on port ${port}`);
});
