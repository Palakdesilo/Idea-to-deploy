import { UIAsset, DocCategory } from '@idea-to-deploy/types';
import { ProjectManager } from './project-manager';

export class AIDesigner {
    private projectManager = new ProjectManager();

    async generateVisuals(projectId: string, description: string): Promise<UIAsset[]> {
        console.log("AIDesigner v4 (Dynamic) - Generating dynamic visuals...");
        const docs = await this.projectManager.getDocs(projectId);
        const uiuxDoc = docs.find(d => (d.category as any) === 'UI_UX');

        const assets: UIAsset[] = [];

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

                // Generate a highly specific prompt for image generation
                const prompt = `Premium UI/UX design for a ${description} application, ${screenName} screen. 
                Features: ${components.join(', ')}. 
                Style: Modern, sleek, high-fidelity mockup, glassmorphism, vibrant colors, professional digital interface, 4k resolution.`;

                // Using a dynamic image generation placeholder service (Pollinations.ai is great for this)
                const encodedPrompt = encodeURIComponent(prompt);
                const imageUrl = `https://pollinations.ai/p/${encodedPrompt}?width=1280&height=720&seed=${index}&nologo=true`;

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
                    promptUsed: prompt,
                    imageUrl
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
                imageUrl: 'https://pollinations.ai/p/Modern%20SaaS%20Dashboard%20UI%20Design%20with%20charts%20and%20analytics?width=1280&height=720&nologo=true'
            } as any);
        }

        return assets;
    }
}


