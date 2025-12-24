export interface Project {
    id: string;
    name: string;
    description: string;
    createdAt: Date;
    status: ProjectStatus;
    metrics: ProjectMetrics;
}

export type ProjectStatus = 'NEW' | 'ANALYSIS' | 'PLANNING' | 'DESIGN' | 'DESIGNED' | 'CODING' | 'COMPLETED' | 'FAILED';

export interface ProjectMetrics {
    progress: number; // 0-100
    currentPhase: string;
    lastUpdated: Date;
}

// The 7 Documentation Categories (PMP-Compliant)
export type DocCategory =
    | 'REQUIREMENTS'
    | 'PLANNING'
    | 'ARCHITECTURE'
    | 'IPMP'
    | 'SCHEDULE_COST'
    | 'QUALITY_RISK'
    | 'TESTING_RELEASE'
    | 'UI_UX';

export interface ScreenDefinition {
    name: string;
    purpose: string;
    roles: string[];
    components: string[];
    interactions: string[];
    states: string[];
}


export interface GeneratedDoc {
    id: string;
    projectId: string;
    category: DocCategory;
    title: string;
    content: string; // Markdown
    isFinal: boolean;
}

export interface Epic {
    id: string;
    projectId: string;
    title: string;
    description: string;
    status: 'TODO' | 'IN_PROGRESS' | 'DONE';
}

export interface UserStory {
    id: string;
    epicId: string;
    title: string;
    acceptanceCriteria: string[];
    points: number;
}

export interface UIAsset {
    id: string;
    projectId: string;
    screenName: string;
    description: string;
    imageUrl?: string;
    promptUsed: string;
    purpose?: string;
    roles?: string[];
    components?: string[];
    interactions?: string[];
    states?: string[];
}


export interface LogEntry {
    timestamp: Date;
    level: 'INFO' | 'WARN' | 'ERROR';
    message: string;
    phase: ProjectStatus;
}
