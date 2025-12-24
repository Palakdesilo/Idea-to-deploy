import * as fs from 'fs-extra';
import * as path from 'path';
import { randomUUID } from 'crypto';
import { Project, ProjectStatus, DocCategory, GeneratedDoc } from '@idea-to-deploy/types';

const DATA_DIR = process.env.DATA_DIR || path.join(process.cwd(), 'data');
const PROJECTS_FILE = path.join(DATA_DIR, 'projects.json');

export class ProjectManager {
    constructor() {
        fs.ensureDirSync(DATA_DIR);
        if (!fs.existsSync(PROJECTS_FILE)) {
            fs.writeJsonSync(PROJECTS_FILE, []);
        }
    }

    async createProject(name: string, description: string): Promise<Project> {
        const projects = await this.getAllProjects();
        const newProject: Project = {
            id: randomUUID(),
            name,
            description,
            createdAt: new Date(),
            status: 'NEW',
            metrics: {
                progress: 0,
                currentPhase: 'Initialization',
                lastUpdated: new Date()
            }
        };
        projects.push(newProject);
        await this.saveProjects(projects);

        // Create project artifacts folder
        const projectDir = path.join(DATA_DIR, 'artifacts', newProject.id);
        await fs.ensureDir(projectDir);

        return newProject;
    }

    async getAllProjects(): Promise<Project[]> {
        return fs.readJson(PROJECTS_FILE);
    }

    async getProject(id: string): Promise<Project | undefined> {
        const projects = await this.getAllProjects();
        return projects.find(p => p.id === id);
    }

    async updateProjectStatus(id: string, status: ProjectStatus): Promise<void> {
        const projects = await this.getAllProjects();
        const project = projects.find(p => p.id === id);
        if (project) {
            project.status = status;
            project.metrics.lastUpdated = new Date();
            await this.saveProjects(projects);
        }
    }

    async getDocs(projectId: string): Promise<GeneratedDoc[]> {
        const docsFile = path.join(DATA_DIR, 'artifacts', projectId, 'docs.json');
        if (!fs.existsSync(docsFile)) return [];
        return fs.readJson(docsFile);
    }

    async saveDoc(projectId: string, category: DocCategory, title: string, content: string): Promise<GeneratedDoc> {
        const docId = randomUUID();
        const doc: GeneratedDoc = {
            id: docId,
            projectId,
            category,
            title,
            content,
            isFinal: true
        };

        // Save to file system specific to project
        const docPath = path.join(DATA_DIR, 'artifacts', projectId, 'docs', `${category.toLowerCase()}.json`);
        await fs.ensureFile(docPath);

        // Actually, let's just use a simple JSON Array for now in docs.json
        const docsFile = path.join(DATA_DIR, 'artifacts', projectId, 'docs.json');
        if (!fs.existsSync(docsFile)) await fs.writeJson(docsFile, []);

        const docs = await fs.readJson(docsFile);
        // Remove old doc of same category if exists
        const filtered = docs.filter((d: GeneratedDoc) => d.category !== category);
        filtered.push(doc);
        await fs.writeJson(docsFile, filtered);
        return doc;
    }

    async getVisuals(projectId: string): Promise<any[]> {
        const visualsFile = path.join(DATA_DIR, 'artifacts', projectId, 'visuals.json');
        if (!fs.existsSync(visualsFile)) return [];
        return fs.readJson(visualsFile);
    }

    async saveVisuals(projectId: string, visuals: any[]): Promise<void> {
        const visualsFile = path.join(DATA_DIR, 'artifacts', projectId, 'visuals.json');
        await fs.writeJson(visualsFile, visuals);
    }

    async getBuildResult(projectId: string): Promise<any | null> {
        const buildFile = path.join(DATA_DIR, 'artifacts', projectId, 'build.json');
        if (!fs.existsSync(buildFile)) return null;
        return fs.readJson(buildFile);
    }

    async saveBuildResult(projectId: string, buildResult: any): Promise<void> {
        const buildFile = path.join(DATA_DIR, 'artifacts', projectId, 'build.json');
        await fs.writeJson(buildFile, buildResult);
    }

    async deleteProject(id: string): Promise<void> {
        const projects = await this.getAllProjects();
        const updatedProjects = projects.filter(p => p.id !== id);

        await this.saveProjects(updatedProjects);

        // Delete artifacts
        const projectDir = path.join(DATA_DIR, 'artifacts', id);
        await fs.remove(projectDir);
    }

    private async saveProjects(projects: Project[]): Promise<void> {
        await fs.writeJson(PROJECTS_FILE, projects, { spaces: 2 });
    }
}
