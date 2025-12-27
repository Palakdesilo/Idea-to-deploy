import { DocCategory } from '@idea-to-deploy/types';
import { LLMService } from './llm-service';
import {
    CANONICAL_JSON_PROMPT,
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
    public static readonly VERSION = '2.0.0';
    private llm = new LLMService();

    async analyzeIdea(idea: string): Promise<Map<DocCategory, string>> {
        const docs = new Map<DocCategory, string>();

        // STEP 1: IDEA -> CANONICAL JSON
        console.log("AIAnalyst: Generating Canonical JSON...");
        const canonicalJsonRaw = await this.llm.generateContent(
            'CANONICAL_JSON',
            { idea },
            CANONICAL_JSON_PROMPT
        );

        // Basic validation and cleaning of JSON
        let canonicalJson = canonicalJsonRaw.trim();
        // Remove markdown formatting if present
        if (canonicalJson.startsWith('```json')) {
            canonicalJson = canonicalJson.replace(/```json\n?/, '').replace(/\n?```/, '');
        } else if (canonicalJson.startsWith('```')) {
            canonicalJson = canonicalJson.replace(/```\n?/, '').replace(/\n?```/, '');
        }

        try {
            JSON.parse(canonicalJson);
            console.log("AIAnalyst: Canonical JSON validated successfully.");
        } catch (e) {
            console.error("AIAnalyst: Failed to parse canonical JSON. Proceeding with raw output but it may affect downstream documents.", e);
        }

        const variables = {
            canonical_json: canonicalJson
        };

        // STEP 2: DOCUMENT GENERATION
        console.log("AIAnalyst: Generating 8 project documents...");

        // We run these in parallel for efficiency
        const [
            requirements,
            planning,
            architecture,
            ipmp,
            scheduleCost,
            qualityRisk,
            testingRelease,
            uiux
        ] = await Promise.all([
            this.llm.generateContent('REQUIREMENTS', variables, REQUIREMENT_PROMPT),
            this.llm.generateContent('PLANNING', variables, PLANNING_PROMPT),
            this.llm.generateContent('ARCHITECTURE', variables, ARCHITECTURE_PROMPT),
            this.llm.generateContent('IPMP', variables, IPMP_PROMPT),
            this.llm.generateContent('SCHEDULE_COST', variables, SCHEDULE_COST_PROMPT),
            this.llm.generateContent('QUALITY_RISK', variables, QUALITY_RISK_PROMPT),
            this.llm.generateContent('TESTING_RELEASE', variables, TESTING_RELEASE_PROMPT),
            this.llm.generateContent('UI_UX', variables, UI_UX_PROMPT)
        ]);

        docs.set('REQUIREMENTS', requirements);
        docs.set('PLANNING', planning);
        docs.set('ARCHITECTURE', architecture);
        docs.set('IPMP', ipmp);
        docs.set('SCHEDULE_COST', scheduleCost);
        docs.set('QUALITY_RISK', qualityRisk);
        docs.set('TESTING_RELEASE', testingRelease);
        docs.set('UI_UX', uiux);

        return docs;
    }
}
