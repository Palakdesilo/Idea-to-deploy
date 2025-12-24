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
        const { idea, features, category, project_complexity, creator_name, expected_start_time } = variables;
        const featureList = (features || 'Core system functionality').split(',').map(f => f.trim());

        if (promptName === 'REQUIREMENTS') {
            return `# 1. Document Control & Versioning
**Author**: ${creator_name || 'Idea-to-Deploy Platform'}
**Date**: ${expected_start_time || new Date().toISOString().split('T')[0]}
**Version**: 1.0.0 (Baseline)

# 2. Project Background & Objectives
This project, **${idea}**, is designed to deliver a high-quality solution in the **${category}** domain. The primary objective is to streamline operations and provide value through specialized features.

# 3. Stakeholder Identification
- **Project Sponsor**: ${creator_name || 'Business Stakeholder'}
- **Technical Lead**: AI Architect
- **End Users**: Users interacting with ${category} services.

# 4. Assumptions & Constraints
- **Assumption**: Scalable cloud infrastructure is available for deployment.
- **Constraint**: Delivery within a 12-week timeframe as per standard PMP guidelines.

# 5. In-Scope / Out-of-Scope
- **In-Scope**: Implementation of ${featureList.slice(0, 3).join(', ')} and core ${category} logic.
- **Out-of-Scope**: Physical hardware procurement and third-party legacy data cleaning.

# 6. Functional Requirements
${featureList.map((f, i) => `## REQ-00${i + 1}: ${f}
The system shall provide robust ${f} capabilities to support the core functionality of ${idea}.`).join('\n\n')}

# 7. Non-Functional Requirements
- **NFR-001 (Performance)**: The ${idea} system must load within 2 seconds.
- **NFR-002 (Security)**: All data for ${category} must be encrypted at rest and in transit.

# 8. User Roles & Permissions
- **Admin**: Full access to manage the ${idea} platform.
- **Standard User**: Access to core ${category} features.

# 9. Business Rules
Data integrity must be maintained across all **${category}** transactions.

# 10. Use Cases / User Stories
- **US-001**: As a user, I want to use ${featureList[0] || 'the system'} so that I can achieve my task in ${idea}.

# 11. UI/UX & Screen References
The interface will follow modern design principles tailored for the **${category}** industry.

# 12. Data Requirements
Relational database storage optimized for **${category}** data entities.

# 13. Regulatory & Compliance Requirements
Compliance with industry standards relevant to **${category}** and GDPR.

# 14. Requirement Traceability Matrix (RTM)
Linking all functional requirements (REQ-001 to REQ-00${featureList.length}) to business objectives.
`;
        }

        if (promptName === 'PLANNING') {
            return `# 1. Project Overview
Project **${idea}** is a ${project_complexity} complexity project in the **${category}** sector.

# 2. Project Governance Structure
Strict PMP-based governance with a Project Manager overseeing the implementation of ${idea}.

# 3. Project Organization & Roles
- **Project Manager**: Managing the 12-week schedule.
- **Developers**: Implementing ${featureList.join(', ')}.

# 4. Project Methodology (Agile)
Agile Scrum methodology with 2-week sprints to iterate on **${idea}** features.

# 5. Work Breakdown Structure (WBS)
- **Phase 1**: Initial Analysis & ${category} Domain Research
- **Phase 2**: Development of ${featureList.slice(0, Math.ceil(featureList.length / 2)).join(', ')}
- **Phase 3**: Integration of remaining features
- **Phase 4**: Final Testing & Deployment of ${idea}

# 6. Deliverables & Milestones
- **MS-1**: Requirement Sign-off (Week 2)
- **MS-2**: ${category} MVP Completion (Week 8)
- **MS-3**: Final Handover of **${idea}** (Week 12)

# 7. Resource Planning
Engineers specializing in **${category}** technology stack and cloud architects.

# 8. Communication Management Plan
Bi-weekly status meetings regarding **${idea}** progress.

# 9. Change Management Plan
Standard change request process for any scope adjustments in the **${idea}** roadmap.

# 10. Dependency Management
Depends on the completion of the core **${category}** engine.

# 11. Assumptions & Constraints
Assumes availability of ${category} domain experts for validation.
`;
        }

        if (promptName === 'IPMP') {
            return `# 1. IPMP Purpose & Scope
This Integrated Project Management Plan defines the execution strategy for **${idea}**.

# 2. Project Objectives & Success Criteria
- **Objective**: Successful deployment of ${idea} with ${featureList.length} core features.
- **Success Criteria**: User acceptance of the ${category} workflow.

# 3. Integrated Baselines (Scope, Schedule, Cost)
A unified baseline for **${idea}** ensure alignment between scope and the 12-week schedule.

# 4. Governance & Decision Framework
Escalation matrix focused on ${category} industry standards.

# 5. Integrated Change Control
Ensures that adding new features to **${idea}** is evaluated for impact on the ${category} delivery.

# 6. Risk, Quality & Procurement Integration
Integrated management of all ${idea} project facets.

# 7. Stakeholder Engagement Strategy
Regular demos of **${category}** components.

# 8. Performance Measurement (KPIs, EV, Metrics)
Tracking velocity of the development of ${featureList[0]} and other modules.

# 9. Reporting & Review Cadence
Phased reviews at each milestone of **${idea}**.

# 10. Escalation & Issue Resolution
Defined path for resolving technical blockers in the **${idea}** stack.

# 11. Compliance & Audit Strategy
Adherence to ${category} compliance standards.
`;
        }

        if (promptName === 'ARCHITECTURE') {
            const stack = category === 'E-commerce' || category === 'SaaS / Subscription'
                ? 'Next.js, Node.js, PostgreSQL, Stripe Integration'
                : 'Next.js, Node.js, PostgreSQL, TailwindCSS';

            return `# 1. Architecture Overview
Technical architecture design for **${idea}**, optimized for the **${category}** domain.

# 2. System Context Diagram
Shows how ${idea} interacts with users and external ${category} APIs.

# 3. Logical Architecture
Breakdown of the system into frontend, backend, and ${category}-specific services.

# 4. Physical Architecture
Hosted on scalable cloud infrastructure to support the ${project_complexity} nature of **${idea}**.

# 5. Technology Stack
Utilizing: ${stack}.

# 6. Application Architecture
Modular design pattern to separate ${featureList.slice(0, 3).join(', ')} from core platform logic.

# 7. Database & Data Flow Design
Schema design for **${idea}** entities including users and ${category} specific data.

# 8. API & Integration Strategy
Secure RESTful endpoints for ${idea} communication.

# 9. Security Architecture
JWT-based authentication and role-based access for ${idea} users.

# 10. Scalability & Performance Design
Load balancing to handle ${category} traffic spikes.

# 11. Deployment Architecture
Automated CI/CD pipeline for rapid ${idea} iterations.

# 12. Technical Risks & Mitigations
Risk: Integration delay with ${category} third-party tools.
Mitigation: Early prototyping of external interfaces.
`;
        }

        if (promptName === 'SCHEDULE_COST') {
            return `# 1. Schedule Management Approach
Methodology for managing the timeline of **${idea}**.

# 2. Project Timeline & Milestones
High-level roadmap for ${idea}: 12 weeks total.

# 3. Task Dependencies
Core ${category} engine must be completed before UI integration.

# 4. Resource Allocation
Staffing plan including ${category} specialists.

# 5. Critical Path Analysis
The development of ${featureList[0] || 'core features'} is on the critical path for **${idea}**.

# 6. Cost Estimation Methodology
Bottom-up estimation based on the ${project_complexity} nature of **${idea}**.

# 7. Budget Breakdown (CAPEX / OPEX)
Infrastructure costs for hosting **${idea}** and development labor.

# 8. Cost Baseline
Approved budget for the delivery of ${idea}.

# 9. Cost Control & Tracking
Monthly tracking of expenses against the **${category}** project budget.

# 10. Earned Value Management (EVM)
Measuring performance against the planned schedule for **${idea}**.

# 11. Schedule & Cost Risks
Risk: Scope creep in **${category}** features affecting the ${idea} budget.
`;
        }

        if (promptName === 'QUALITY_RISK') {
            return `# 1. Quality Management
Quality philosophy for the **${idea}** project.

# 2. Quality Objectives
Ensuring a bug-free experience for ${category} users.

# 3. Quality Standards & Metrics
Code coverage and performance targets for **${idea}**.

# 4. Quality Assurance Process
Defect prevention during the development of ${featureList.slice(0, 2).join(' and ')}.

# 5. Quality Control Activities
Continuous integration and manual testing of **${idea}**.

# 6. Risk Management
Identifying risks specific to the **${category}** domain.

# 7. Risk Identification
- RISK-001: Data privacy issues in ${idea}.
- RISK-002: Scaling challenges for the ${category} platform.

# 8. Risk Register
Comprehensive log of all identified risks for **${idea}**.

# 9. Risk Analysis & Prioritization
Focusing on high-impact risks to the ${idea} launch.

# 10. Risk Response Strategies
Mitigation plans for technical hurdles in **${idea}**.

# 11. Procurement Management
Sourcing strategy for **${idea}** external dependencies.

# 12. Procurement Strategy
Utilizing open-source libraries and cloud services for the **${idea}** tech stack.

# 13. Vendor Selection Criteria
Standards for third-party ${category} service providers.

# 14. Contract Types
Standardized agreements for the **${idea}** vendors.

# 15. SLA & Performance Monitoring
Uptime requirements for the ${idea} production environment.
`;
        }

        if (promptName === 'TESTING_RELEASE') {
            return `# 1. Test Strategy
Testing approach for **${idea}** to ensure ${category} compliance.

# 2. Test Scope & Objectives
Verification of all features including ${featureList.join(', ')}.

# 3. Test Environment Setup
Staging environment mirroring the ${idea} production setup.

# 4. Test Types (Unit, Integration, System, UAT)
Comprehensive testing phases for the **${idea}** platform.

# 5. Test Data Management
Mocking **${category}** data for secure and effective testing.

# 6. Defect Management Process
Bug tracking for all issues found in **${idea}**.

# 7. Entry & Exit Criteria
Milestones that must be met before releasing **${idea}**.

# 8. Release Management Strategy
Phased rollout plan for the ${category} market.

# 9. Deployment Plan
Step-by-step procedure for the **${idea}** go-live.

# 10. Rollback & Recovery Plan
Safety procedures in case of ${idea} deployment failure.

# 11. Post-Release Validation
Smoke tests to confirm ${idea} functionality in production.

# 12. Maintenance & Support Strategy
Post-launch support for users of the **${idea}** platform.
`;
        }

        if (promptName === 'UI_UX') {
            const screens = ['Dashboard', 'User Profile', 'Settings', 'Search Results', 'Detail View'];
            return `# UI/UX Design Specification for ${idea}

${screens.map(s => `### ${s} Screen
- **Purpose**: Providing users with a clear ${s.toLowerCase()} view for ${idea} workflows.
- **Roles**: Admin, Standard User
- **Components**: Header, Navigation, Main Content Area, Footer
- **Interactions**: Click-through navigation and data interaction.
- **States**: Loading, Active, Empty`).join('\n\n')}
`;
        }

        // Default detail for other sections
        return `# ${promptName} Document for ${idea}
        
This document contains the professional-grade ${promptName} specifications for your **${category}** project. It is designed to be actionable, measurable, and auditable.

**Details:**
- Complexity: ${project_complexity || 'Enterprise'}
- Feature Set: ${features}
- Compliance: PMBOK / PMP Standards
`;
    }
}
