
export const REQUIREMENT_PROMPT = `
You are a PMP-certified Software Project Consultant.
Create a **complete Requirement Document** for the project: {idea}.
**Project Category**: {category}
**Core Features**: {features}
**Complexity**: {project_complexity}

**CRITICAL: YOU MUST USE THESE EXACT 14 SECTIONS IN THIS EXACT ORDER.**

**REQUIRED STRUCTURE:**
1. **Document Control & Versioning**
2. **Project Background & Objectives**
3. **Stakeholder Identification**
4. **Assumptions & Constraints**
5. **In-Scope / Out-of-Scope**
6. **Functional Requirements**
7. **Non-Functional Requirements**
8. **User Roles & Permissions**
9. **Business Rules**
10. **Use Cases / User Stories**
11. **UI/UX & Screen References**
12. **Data Requirements**
13. **Regulatory & Compliance Requirements**
14. **Requirement Traceability Matrix (RTM)**

**Section Details:**
1. **Document Control & Versioning**: Version history, Author: {creator_name}, Date: {expected_start_time}.
2. **Project Background & Objectives**: Why this project exists and what it aims to achieve for {idea} in the {category} domain.
3. **Stakeholder Identification**: List of key stakeholders and their roles specific to a {category} application.
4. **Assumptions & Constraints**: Technical or business assumptions and limitations for {idea}.
5. **In-Scope / Out-of-Scope**: Clearly define what is being built (including {features}) and what is not.
6. **Functional Requirements**: Detailed list of features with IDs (REQ-001, etc.), focusing on {features}.
7. **Non-Functional Requirements**: Performance, Security, Reliability with IDs (NFR-001, etc.) tailored for a {category} product.
8. **User Roles & Permissions**: Define user types (e.g., Admin, Customer) and what they can do in {idea}.
9. **Business Rules**: Logic governing the system behavior for {category} workflows.
10. **Use Cases / User Stories**: Detailed US-001/UC-001 stories for key features like {features}.
11. **UI/UX & Screen References**: Descriptions of key screens and interactions for {idea}.
12. **Data Requirements**: Data models, entities, and storage needs for {category} data.
13. **Regulatory & Compliance Requirements**: Legal or industry standards (GDPR, etc.) for {category}.
14. **Requirement Traceability Matrix (RTM)**: Mapping requirements to business goals and testing.

Use professional, formal language. No placeholders. Ensure every section reflects the specific nature of {idea}.
`;

export const PLANNING_PROMPT = `
You are a PMP-certified Software Project Consultant.
Create a **complete Project Planning Document** for the project: {idea}.
**Project Category**: {category}
**Core Features**: {features}
**Complexity**: {project_complexity}

**REQUIRED STRUCTURE:**
1. **Project Overview**
2. **Project Governance Structure**
3. **Project Organization & Roles**
4. **Project Methodology (Agile, Hybrid, Waterfall)**
5. **Work Breakdown Structure (WBS)**
6. **Deliverables & Milestones**
7. **Resource Planning**
8. **Communication Management Plan**
9. **Change Management Plan**
10. **Dependency Management**
11. **Assumptions & Constraints**

**Section Details:**
1. **Project Overview**: High level summary of the plan for {idea}.
2. **Project Governance Structure**: Decision making process and oversight for this {project_complexity} project.
3. **Project Organization & Roles**: Team structure and responsibilities needed for {category} development.
4. **Project Methodology**: Justification for choosing Agile, Hybrid, or Waterfall for {idea}.
5. **Work Breakdown Structure (WBS)**: Hierarchical decomposition of work for implementing {features}.
6. **Deliverables & Milestones**: Key outputs and dates for the 12-week {idea} roadmap.
7. **Resource Planning**: Human and technical resources needed for {category} tech stack.
8. **Communication Management Plan**: How stakeholders will be kept informed.
9. **Change Management Plan**: Process for handling scope changes in {idea}.
10. **Dependency Management**: Internal and external dependencies (e.g., APIs, Cloud).
11. **Assumptions & Constraints**: Planning-specific assumptions for {idea}.

Ensure all sections are comprehensive, actionable, and specific to the {category} domain.
`;

export const ARCHITECTURE_PROMPT = `
You are a Senior System Architect.
Create a **Technical Architecture & Delivery Plan** for the project: {idea}.
**Project Category**: {category}
**Core Features**: {features}
**Complexity**: {project_complexity}

**REQUIRED STRUCTURE:**
1. **Architecture Overview**
2. **System Context Diagram**
3. **Logical Architecture**
4. **Physical Architecture**
5. **Technology Stack**
6. **Application Architecture**
7. **Database & Data Flow Design**
8. **API & Integration Strategy**
9. **Security Architecture**
10. **Scalability & Performance Design**
11. **Deployment Architecture**
12. **Technical Risks & Mitigations**

**Section Details:**
1. **Architecture Overview**: The architectural philosophy for a {category} application like {idea}.
2. **System Context Diagram**: How {idea} interacts with external entities (Users, 3rd party APIs).
3. **Logical Architecture**: System components and their relationships for {features}.
4. **Physical Architecture**: Hosting, servers, and network topology for a {project_complexity} system.
5. **Technology Stack**: Recommended Backend, Frontend, DB, and DevOps tools for {category}.
6. **Application Architecture**: Design patterns (Microservices, Monolith, etc.) suitable for {idea}.
7. **Database & Data Flow Design**: Schema overview and data movement for {features}.
8. **API & Integration Strategy**: REST/GraphQL, Third-party integrations (e.g., Payments, Auth).
9. **Security Architecture**: Auth, Encryption, Threat modeling for {category} data.
10. **Scalability & Performance Design**: How {idea} handles load for its target audience.
11. **Deployment Architecture**: CI/CD, Containerization, Orchestration.
12. **Technical Risks & Mitigations**: Potential technical hurdles for {category} and their solutions.

Deliver a technical blueprint that is ready for implementation.
`;

export const IPMP_PROMPT = `
You are a PMP-certified Software Project Consultant.
Create an **Integrated Project Management Plan (IPMP)** for the project: {idea}.
**Project Category**: {category}
**Core Features**: {features}
**Complexity**: {project_complexity}

**REQUIRED STRUCTURE:**
1. **IPMP Purpose & Scope**
2. **Project Objectives & Success Criteria**
3. **Integrated Baselines (Scope, Schedule, Cost)**
4. **Governance & Decision Framework**
5. **Integrated Change Control**
6. **Risk, Quality & Procurement Integration**
7. **Stakeholder Engagement Strategy**
8. **Performance Measurement (KPIs, EV, Metrics)**
9. **Reporting & Review Cadence**
10. **Escalation & Issue Resolution**
11. **Compliance & Audit Strategy**

**Section Details:**
1. **IPMP Purpose & Scope**: Why this integrated plan exists for {idea}.
2. **Project Objectives & Success Criteria**: Specific, measurable targets for {category} success.
3. **Integrated Baselines**: Summary of scope (for {features}), time (12 weeks), and budget.
4. **Governance & Decision Framework**: Who decides what for this {project_complexity} project.
5. **Integrated Change Control**: How changes are managed across all plans for {idea}.
6. **Risk, Quality & Procurement Integration**: How these areas interact in the {category} space.
7. **Stakeholder Engagement Strategy**: Keeping people involved in the {idea} journey.
8. **Performance Measurement**: KPIs and metrics for {features} development.
9. **Reporting & Review Cadence**: Frequency of audits and reports for {idea}.
10. **Escalation & Issue Resolution**: Path for solving problems in {category} development.
11. **Compliance & Audit Strategy**: Ensuring standards are met for {idea}.

This document must unify all project facets into a single source of truth.
`;

export const SCHEDULE_COST_PROMPT = `
You are a Project Planner and Financial Analyst.
Create a **Schedule & Cost Plan** for the project: {idea}.
**Project Category**: {category}
**Core Features**: {features}
**Complexity**: {project_complexity}

**REQUIRED STRUCTURE:**
1. **Schedule Management Approach**
2. **Project Timeline & Milestones**
3. **Task Dependencies**
4. **Resource Allocation**
5. **Critical Path Analysis**
6. **Cost Estimation Methodology**
7. **Budget Breakdown (CAPEX / OPEX)**
8. **Cost Baseline**
9. **Cost Control & Tracking**
10. **Earned Value Management (EVM)**
11. **Schedule & Cost Risks**

**Section Details:**
1. **Schedule Management Approach**: How time will be managed for {idea}.
2. **Project Timeline & Milestones**: Specific dates and phases for {category} delivery.
3. **Task Dependencies**: What must happen before what in {features} implementation.
4. **Resource Allocation**: Budgeting for people and tools in the {category} stack.
5. **Critical Path Analysis**: Identifying the most important tasks for {idea} success.
6. **Cost Estimation**: How costs were calculated for this {project_complexity} project.
7. **Budget Breakdown**: Capital vs Operational expenses for {idea}.
8. **Cost Baseline**: The approved budget for {category} development.
10. **Earned Value Management (EVM)**: Performance measurement technique for {idea}.
11. **Schedule & Cost Risks**: Financial and timing risks specific to {category}.

Ensure the plan is realistic and covers the full 12-week lifecycle.
`;

export const QUALITY_RISK_PROMPT = `
You are a Quality Assurance and Risk Manager.
Create a **Quality, Risk & Procurement Plan** for the project: {idea}.
**Project Category**: {category}
**Core Features**: {features}
**Complexity**: {project_complexity}

**REQUIRED STRUCTURE:**
1. **Quality Management**
2. **Quality Objectives**
3. **Quality Standards & Metrics**
4. **Quality Assurance Process**
5. **Quality Control Activities**
6. **Risk Management**
7. **Risk Identification**
8. **Risk Register**
9. **Risk Analysis & Prioritization**
10. **Risk Response Strategies**
11. **Procurement Management**
12. **Procurement Strategy**
13. **Vendor Selection Criteria**
14. **Contract Types**
15. **SLA & Performance Monitoring**

**Section Details:**
1. **Quality Management**: Overall philosophy for a {category} product.
2. **Quality Objectives**: Targeted quality levels for {features}.
3. **Quality Standards & Metrics**: How quality is measured in {idea}.
4. **Quality Assurance Process**: Preventing defects in {category} logic.
5. **Quality Control Activities**: Detecting defects in {idea}.
6. **Risk Management**: Risk framework for {project_complexity} projects.
7. **Risk Identification**: Specific potential issues for {category} (e.g., Security, Data).
8. **Risk Register**: List of identified risks for {idea}.
10. **Risk Response Strategies**: Mitigation, Avoidance, Transfer, Acceptance.
11. **Procurement Management**: Buying services/products for {category} stack.
12. **Procurement Strategy**: Buy vs Build for {idea} components.

Focus on high-risk areas of {idea}.
`;

export const TESTING_RELEASE_PROMPT = `
You are a QA Lead and Release Manager.
Create a **Testing & Release Plan** for the project: {idea}.
**Project Category**: {category}
**Core Features**: {features}
**Complexity**: {project_complexity}

**REQUIRED STRUCTURE:**
1. **Test Strategy**
2. **Test Scope & Objectives**
3. **Test Environment Setup**
4. **Test Types (Unit, Integration, System, UAT)**
5. **Test Data Management**
6. **Defect Management Process**
7. **Entry & Exit Criteria**
8. **Release Management Strategy**
9. **Deployment Plan**
10. **Rollback & Recovery Plan**
11. **Post-Release Validation**
12. **Maintenance & Support Strategy**

**Section Details:**
1. **Test Strategy**: Overall testing approach for {idea}.
2. **Test Scope & Objectives**: What will and won't be tested in {features}.
3. **Test Environment**: Where testing happens for this {category} app.
4. **Test Types**: Details on Unit, Integration, System, and UAT for {idea}.
5. **Test Data**: Managing data for {category} test cases.
6. **Defect Management**: How bugs are tracked and fixed in {idea}.
7. **Entry & Exit Criteria**: When to start/stop testing for {features}.
8. **Release Management**: How the product is released to {category} users.
9. **Deployment Plan**: Steps to go live for {idea}.
10. **Rollback & Recovery**: What to do if things go wrong during {category} launch.
11. **Post-Release Validation**: Verifying the live {idea} system.
12. **Maintenance & Support**: Post-launch care for {category} users.

Ensure the release plan is robust and minimizes downtime.
`;

export const UI_UX_PROMPT = `
You are a Senior UI/UX Designer.
Create a **Detailed UI/UX Design Specification** for the project: {idea}.
**Project Category**: {category}
**Core Features**: {features}

**CRITICAL: YOUR OUTPUT MUST BE PARSABLE. USE THIS FORMAT FOR EACH SCREEN:**

### [Screen Name] Screen
- **Purpose**: A clear description of why this screen exists.
- **Roles**: Which user roles (from {features}) can access this.
- **Components**: A comma-separated list of UI components (e.g., Header, Sidebar, Search Bar, Card List).
- **Interactions**: User actions available (e.g., Click 'Buy' to add to cart, Drag and Drop to reorder).
- **States**: Different UI states (e.g., Loading, Empty, Error, Success).

**List at least 5-7 key screens for the {idea} project.**
Include a Dashboard, User Profile, and screen-specific workflows for {category}.
Use professional design terminology.
`;
