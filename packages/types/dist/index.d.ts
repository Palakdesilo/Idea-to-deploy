export interface Project {
    id: string;
    name: string;
    description: string;
    createdAt: Date;
    status: ProjectStatus;
    metrics: ProjectMetrics;
}
export type ProjectStatus = 'NEW' | 'ANALYSIS' | 'PLANNING' | 'DESIGN' | 'CODING' | 'COMPLETED' | 'FAILED';
export interface ProjectMetrics {
    progress: number;
    currentPhase: string;
    lastUpdated: Date;
}
export type DocCategory = 'REQUIREMENTS' | 'PLANNING' | 'ARCHITECTURE' | 'MANAGEMENT' | 'SCHEDULE_COST' | 'QUALITY_RISK' | 'TESTING_RELEASE';
export interface GeneratedDoc {
    id: string;
    projectId: string;
    category: DocCategory;
    title: string;
    content: string;
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
}
export interface LogEntry {
    timestamp: Date;
    level: 'INFO' | 'WARN' | 'ERROR';
    message: string;
    phase: ProjectStatus;
}
