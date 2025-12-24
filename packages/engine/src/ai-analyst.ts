import { DocCategory, GeneratedDoc } from '@idea-to-deploy/types';
import { LLMService } from './llm-service';
import {
    REQUIREMENT_PROMPT,
    PLANNING_PROMPT,
    ARCHITECTURE_PROMPT,
    IPMP_PROMPT,
    SCHEDULE_COST_PROMPT,
    QUALITY_RISK_PROMPT,
    TESTING_RELEASE_PROMPT,
    UI_UX_PROMPT
} from './ai-prompts';

export class AIAnalyst {
    public static readonly VERSION = '1.1.0';
    private llm = new LLMService();

    async analyzeIdea(idea: string): Promise<Map<DocCategory, string>> {
        const category = this.inferCategory(idea);
        const features = this.inferFeatures(idea, category);
        const complexity = this.inferComplexity(features);
        const docs = new Map<DocCategory, string>();

        const variables: any = {
            idea,
            category,
            project_domain: category,
            project_complexity: complexity,
            features: features.join(', '),
            creator_name: "Idea-to-Deploy Platform",
            expected_start_time: new Date().toISOString().split('T')[0],
            when_in_doubt_rule: "Provide high-quality, professional, and detailed content that matches the project's industry standards.",
            focus_instruction: "Ensure all sections are comprehensive, actionable, and strictly follow the provided structure.",
            project_name: idea.substring(0, 50)
        };

        // Phase 1: Core Analysis (Requirements & Planning)
        const [requirements, planning] = await Promise.all([
            this.llm.generateContent('REQUIREMENTS', variables, REQUIREMENT_PROMPT),
            this.llm.generateContent('PLANNING', variables, PLANNING_PROMPT)
        ]);

        docs.set('REQUIREMENTS' as DocCategory, requirements);
        docs.set('PLANNING' as DocCategory, planning);

        // Phase 2: Technical & Specialized Plans
        variables.requirement_document = requirements;
        variables.planning_document = planning;

        const [architecture, scheduleCost, qualityRisk] = await Promise.all([
            this.llm.generateContent('ARCHITECTURE', variables, ARCHITECTURE_PROMPT),
            this.llm.generateContent('SCHEDULE_COST', variables, SCHEDULE_COST_PROMPT),
            this.llm.generateContent('QUALITY_RISK', variables, QUALITY_RISK_PROMPT)
        ]);

        docs.set('ARCHITECTURE' as DocCategory, architecture);
        docs.set('SCHEDULE_COST' as DocCategory, scheduleCost);
        docs.set('QUALITY_RISK' as DocCategory, qualityRisk);

        // Phase 3: Final Integration & Release
        variables.technical_architecture_document = architecture;

        const [ipmp, testingRelease, uiux] = await Promise.all([
            this.llm.generateContent('IPMP', variables, IPMP_PROMPT),
            this.llm.generateContent('TESTING_RELEASE', variables, TESTING_RELEASE_PROMPT),
            this.llm.generateContent('UI_UX', variables, UI_UX_PROMPT)
        ]);

        docs.set('IPMP' as DocCategory, ipmp);
        docs.set('TESTING_RELEASE' as DocCategory, testingRelease);
        docs.set('UI_UX' as DocCategory, uiux);

        return docs;
    }

    private inferComplexity(features: string[]): string {
        if (features.length > 15) return 'Enterprise';
        if (features.length > 10) return 'Complex';
        if (features.length > 5) return 'Moderate';
        return 'Simple';
    }

    private inferCategory(idea: string): string {
        const i = idea.toLowerCase();
        if (i.includes('shop') || i.includes('e-commerce') || i.includes('store') || i.includes('sell')) return 'E-commerce';
        if (i.includes('social') || i.includes('chat') || i.includes('community') || i.includes('network')) return 'Social Media';
        if (i.includes('saas') || i.includes('platform') || i.includes('subscription') || i.includes('tool')) return 'SaaS / Subscription';
        if (i.includes('booking') || i.includes('reserve') || i.includes('hotel') || i.includes('flight')) return 'Booking System';
        return 'General Web Application';
    }

    private inferFeatures(idea: string, category: string): string[] {
        const defaults = ['User Registration', 'Login', 'Logout', 'Forgot Password', 'Profile Management'];
        const specific: string[] = [];

        if (category === 'E-commerce') {
            specific.push('Product Listing', 'Shopping Cart', 'Checkout', 'Order Management', 'Payment Integration');
        } else if (category === 'Social Media') {
            specific.push('Feed / Posts', 'Likes & Comments', 'Messaging', 'User Profiles', 'Notifications');
        } else if (category === 'SaaS / Subscription') {
            specific.push('Subscription Plans', 'Billing & Invoices', 'Feature Access Control', 'Analytics Dashboard');
        } else if (category === 'Booking System') {
            specific.push('Search / Filter', 'Booking Calendar', 'Payment Processing', 'Booking History');
        }

        if (idea.toLowerCase().includes('admin')) specific.push('Admin Dashboard', 'User Management');
        if (idea.toLowerCase().includes('search')) specific.push('Advanced Search');

        return [...new Set([...defaults, ...specific])];
    }
}
