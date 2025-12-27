// LLM Service with robust fallback and optional dependency loading
export class LLMService {
    private model: any = null;
    private langchainReady: boolean = false;

    constructor() {
        this.initializeLangChain();
    }

    private async initializeLangChain() {
        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey) return;

        try {
            // Dynamic check for langchain availability to prevent build/runtime crashes
            const { ChatOpenAI } = require("@langchain/openai");
            this.model = new ChatOpenAI({
                openAIApiKey: apiKey,
                modelName: "gpt-4-turbo-preview",
                temperature: 0.7,
            });
            this.langchainReady = true;
        } catch (error) {
            console.warn("LangChain modules not found or could not be initialized. Using advanced PMP fallback.");
        }
    }

    async generateContent(promptName: string, variables: Record<string, string>, template: string): Promise<string> {
        if (this.langchainReady && this.model) {
            try {
                const { PromptTemplate } = require("@langchain/core/prompts");
                const { StringOutputParser } = require("@langchain/core/output_parsers");
                const { RunnableSequence } = require("@langchain/core/runnables");

                const prompt = PromptTemplate.fromTemplate(template);
                const chain = RunnableSequence.from([
                    prompt,
                    this.model,
                    new StringOutputParser(),
                ]);

                return await chain.invoke(variables);
            } catch (error) {
                console.warn(`LLM Generation failed for ${promptName}, falling back:`, error);
                return this.fallbackGeneration(promptName, variables);
            }
        } else {
            return this.fallbackGeneration(promptName, variables);
        }
    }

    private fallbackGeneration(promptName: string, variables: Record<string, string>): string {
        let { idea, canonical_json } = variables;
        let jsonData: any = null;

        if (canonical_json) {
            try {
                jsonData = JSON.parse(canonical_json);
            } catch (e) {
                console.warn("Fallback: Failed to parse canonical_json");
            }
        }

        if (promptName === 'CANONICAL_JSON') {
            return JSON.stringify({
                project_overview: {
                    summary: idea || "A new digital solution",
                    problem_statement: "Manual processes are inefficient",
                    objectives: ["Automate workflows", "Improve user experience", "Provide data insights"]
                },
                users: {
                    target_users: ["Standard Users", "System Administrators"],
                    user_roles: ["User", "Admin"]
                },
                scope: {
                    in_scope: ["Web interface", "Core database", "User authentication"],
                    out_of_scope: ["Mobile application", "Offline mode", "Legacy system migration"]
                },
                features: {
                    must_have: ["User Dashboard", "Data Entry Forms", "Reporting Module"],
                    nice_to_have: ["Dark Mode", "Push Notifications", "Advanced Analytics"]
                },
                constraints: {
                    time: "12 weeks",
                    budget: "Enterprise standard",
                    technical: "Modern web stack",
                    regulatory: "GDPR Compliance"
                },
                assumptions: ["Internet connectivity is available", "Users have basic technical proficiency"],
                risks: ["Integration challenges", "Data security vulnerabilities"],
                success_metrics: ["90% user adoption", "Reduced processing time"],
                scalability_expectations: "Support up to 10,000 concurrent users"
            }, null, 2);
        }

        const summary = jsonData?.project_overview?.summary || idea || 'Project Alpha';
        const features = jsonData?.features?.must_have || ['User Management', 'Dashboard', 'Data Analytics'];
        const roles = jsonData?.users?.user_roles || ['Admin', 'User'];
        const objectives = jsonData?.project_overview?.objectives || ['Deliver high value', 'Ensure security'];

        if (promptName === 'REQUIREMENTS') {
            return `# Requirement Specification: ${summary}
            
## Purpose
To define the functional and non-functional requirements for the ${summary} system.

## Scope
Includes development of ${features.join(', ')}.

## User Roles
${roles.map((r: string) => `- **${r}**: Primary user role.`).join('\n')}

## Functional Requirements
${features.map((f: string, i: number) => `### FR-0${i + 1}: ${f}
The system shall provide ${f} functionality.`).join('\n\n')}

## Non-Functional Requirements
- **Performance**: System responds within 200ms.
- **Security**: OAuth2 based authentication.

## Assumptions
- Stable network environment.

## Constraints
- Completion within 12 weeks.

## Dependencies
- Cloud provider availability.
`;
        }

        if (promptName === 'PLANNING') {
            return `# Project Planning: ${summary}

## Project Goals
${objectives.map((o: string) => `- ${o}`).join('\n')}

## Deliverables
- Functional Prototype
- Production-Ready Codebase
- Technical Documentation

## Project Phases
1. Initial Analysis
2. Core Development
3. Quality Assurance
4. Launch

## Milestones
- M1: Scope Definition (Week 2)
- M2: MVP Completion (Week 8)
- M3: Final Release (Week 12)

## Resource Overview
- 2 Full-stack Developers
- 1 UI/UX Designer
- 1 QA Engineer

## Communication Plan
Weekly stakeholder updates via email and bi-weekly demo calls.
`;
        }

        if (promptName === 'ARCHITECTURE') {
            return `# Technical Architecture: ${summary}

## System Overview
A robust, scalable web architecture designed for ${summary}.

## High-Level Architecture
Layered architecture: Presentation, Logic, and Data.

## Technology Stack
- **Frontend**: React / Next.js
- **Backend**: Node.js / Express
- **Database**: PostgreSQL
- **Infrastructure**: AWS / Vercel

## Data Flow Overview
Users interact with Frontend -> API calls to Backend -> Transactional data in Database.

## Security Considerations
- TLS 1.3 Encryption
- JWT Session Management
- Role-based Access Control

## Scalability Strategy
Horizontal scaling using containerized microservices.

## Deployment Overview
Automated CI/CD pipeline with Blue/Green deployment strategy.
`;
        }

        if (promptName === 'IPMP') {
            return `# Integrated Project Management Plan (IPMP): ${summary}

## Project Overview
Consolidated execution strategy for the ${summary} project.

## Governance Structure
Project Sponsor -> Project Manager -> Technical Team.

## Scope Management
Change requests evaluated by CCB (Change Control Board).

## Schedule Management
12-week timeline with bi-weekly sprints.

## Cost Management
Managed within the enterprise operational budget.

## Quality Management
Unit tests, integration tests, and UAT.

## Risk Management
Continuous monitoring and mitigation of technical risks.

## Change Control
Version-controlled codebase and documented requirement changes.

## Communication Management
Centralized project dashboard for all stakeholders.
`;
        }

        if (promptName === 'SCHEDULE_COST') {
            return `# Schedule & Cost Estimation: ${summary}

## Work Breakdown Structure (High-Level)
1. Environment Setup
2. Module Development (${features.slice(0, 2).join(', ')})
3. Integration
4. Testing

## Estimated Timeline
12 weeks total execution time.

## Resource Effort Estimates
- Dev: 480 hours
- QA: 160 hours
- PM: 80 hours

## Cost Breakdown
- Labor: $60,000
- Infrastructure: $5,000
- Licenses: $2,000

## Contingency Planning
15% budget buffer for unforeseen technical challenges.
`;
        }

        if (promptName === 'QUALITY_RISK') {
            return `# Quality & Risk Management: ${summary}

## Quality Objectives
Zero critical bugs at launch; 99.9% uptime.

## Quality Standards
ISO/IEC 25010 Software Quality Standards.

## Review & Approval Process
Peer code reviews and automated linting.

## Risk Register
- RISK-01: Delay in 3rd party API (Medium)
- RISK-02: Data breach (Low probability, High impact)

## Risk Mitigation Plan
Early prototyping and rigorous security audits.
`;
        }

        if (promptName === 'TESTING_RELEASE') {
            return `# Testing Strategy: ${summary}

## Test Strategy
Risk-based testing approaching focused on critical paths.

## Test Types
- Unit Testing
- Integration Testing
- System Integration (SIT)
- User Acceptance (UAT)

## Test Scenarios (High-Level)
- Successful user login
- ${features[0]} execution
- Error handling on invalid input

## Entry & Exit Criteria
- Entry: 100% code completion
- Exit: 0 critical defects remaining

## Defect Management
Jira-based tracking with prioritization matrix.

## Release Approval
Final sign-off by Product Owner and QA Lead.
`;
        }

        if (promptName === 'UI_UX') {
            const screens = ['Dashboard', 'Detail View', 'Settings', 'Profile', 'Activity Log'];
            return `# UI/UX Design Specification: ${summary}

${screens.map(s => `### ${s} Screen
- **Purpose**: Key interface for ${s}.
- **Roles**: ${roles.join(', ')}
- **Components**: Navigation, Header, Content Area
- **Interactions**: Button clicks, Form submission
- **States**: Loading, Active, Error`).join('\n\n')}
`;
        }

        return `# ${promptName} Document for ${summary}
        
Professional documentation generated for project ${summary}.
`;
    }
}
