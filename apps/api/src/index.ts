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

        await projectManager.updateProjectStatus(project.id, 'DESIGN');

        console.log(`Starting dynamic design generation for: ${project.name}`);

        // Use the AIDesigner engine which has the premium dynamic logic
        const visuals = await aiDesigner.generateVisuals(project.id, project.description);

        // Save and update status
        await projectManager.saveVisuals(project.id, visuals);
        await projectManager.updateProjectStatus(project.id, 'DESIGNED' as any);

        res.json({ success: true, visuals });
    } catch (err: any) {
        console.error('Design generation failed:', err);
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

app.put('/api/projects/:id/build/file', async (req: Request, res: Response) => {
    try {
        const { path, content } = req.body;
        if (!path) return res.status(400).json({ error: 'Path is required' });
        await projectManager.updateFileContent(req.params.id, path, content);
        res.json({ success: true });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(port, () => {
    console.log(`API Server running on port ${port}`);
});
