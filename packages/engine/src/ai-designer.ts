import { UIAsset, DocCategory } from '@idea-to-deploy/types';
import { ProjectManager } from './project-manager';

export class AIDesigner {
    private projectManager = new ProjectManager();

    async generateVisuals(projectId: string, description: string): Promise<UIAsset[]> {
        console.log("AIDesigner v3 (Unsplash) - Generating visuals...");
        const docs = await this.projectManager.getDocs(projectId);
        const uiuxDoc = docs.find(d => (d.category as any) === 'UI_UX');
        const projects = await this.projectManager.getAllProjects();
        const project = projects.find(p => p.id === projectId);
        const desc = project?.description?.toLowerCase() || '';

        let category = 'business-app';
        if (desc.includes('ecommerce') || desc.includes('shop') || desc.includes('store')) category = 'ecommerce';
        else if (desc.includes('social') || desc.includes('chat') || desc.includes('connect')) category = 'social-media';
        else if (desc.includes('game') || desc.includes('play')) category = 'gaming';
        else if (desc.includes('health') || desc.includes('fitness')) category = 'healthcare';
        else if (desc.includes('finance') || desc.includes('bank') || desc.includes('money')) category = 'finance';

        const assets: UIAsset[] = [];

        // Curated high-quality Unsplash UI Mockup IDs
        const uiMockups: Record<string, string[]> = {
            'ecommerce': [
                'https://images.unsplash.com/photo-1557821552-17105176677c', 'https://images.unsplash.com/photo-1472851294608-062f824d29cc',
                'https://images.unsplash.com/photo-1523275335684-37898b6baf30', 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d'
            ],
            'social-media': [
                'https://images.unsplash.com/photo-1611162617474-5b21e879e113', 'https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0',
                'https://images.unsplash.com/photo-1611605851314-72663f9a11d4', 'https://images.unsplash.com/photo-1611606063065-ee7946f0787a'
            ],
            'business-app': [
                'https://images.unsplash.com/photo-1551288049-bebda4e38f71', 'https://images.unsplash.com/photo-1460925895917-afdab827c52f',
                'https://images.unsplash.com/photo-1542744094-24638eff586b', 'https://images.unsplash.com/photo-1551434678-e076c223a692'
            ]
        };

        const selectedMockups = uiMockups[category] || uiMockups['business-app'];

        if (uiuxDoc) {
            const screenSections = uiuxDoc.content.split('### ').slice(1);

            screenSections.forEach((section, index) => {
                const lines = section.split('\n');
                const screenName = lines[0].replace(' Screen', '').trim();

                const purpose = section.match(/- \*\*Purpose\*\*: (.*)/)?.[1] || '';
                const roles = section.match(/- \*\*Roles\*\*: (.*)/)?.[1]?.split(',').map(r => r.trim()) || [];
                const components = section.match(/- \*\*Components\*\*: (.*)/)?.[1]?.split(',').map(c => c.trim()) || [];
                const interactions = section.match(/- \*\*Interactions\*\*: (.*)/)?.[1]?.split(',').map(i => i.trim()) || [];
                const states = section.match(/- \*\*States\*\*: (.*)/)?.[1]?.split(',').map(s => s.trim()) || [];

                const baseImg = selectedMockups[index % selectedMockups.length];

                assets.push({
                    id: crypto.randomUUID(),
                    projectId,
                    screenName,
                    description: purpose || `Interface for ${screenName}`,
                    purpose,
                    roles,
                    components,
                    interactions,
                    states,
                    promptUsed: `Premium UI Mockup for ${screenName}`,
                    imageUrl: `${baseImg}?q=80&w=1200&auto=format&fit=crop`
                } as any);
            });
        }

        if (assets.length === 0) {
            assets.push({
                id: crypto.randomUUID(),
                projectId,
                screenName: 'Dashboard',
                description: 'Overview of system status',
                promptUsed: 'Modern dashboard mockup',
                imageUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=1200&auto=format&fit=crop'
            });
        }

        return assets;
    }
}


