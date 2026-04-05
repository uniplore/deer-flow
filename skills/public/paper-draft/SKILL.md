---
name: paper-draft
description: Use this skill when generating, drafting, or reviewing academic research papers. Triggers on "generate paper", "write research paper", "draft academic paper", "review paper draft", "improve paper", "research idea", "create paper draft", or any academic writing task that involves literature-backed content generation.
---

# Paper Draft Generation Skill

## Overview

This skill provides a systematic multi-stage pipeline for generating high-quality academic research paper drafts. It combines real-time literature retrieval with structured ideation, multi-perspective review, and iterative refinement to produce publication-ready drafts.

## When to Use This Skill

- User asks to generate, write, or create a research paper draft
- User provides a research topic or keyword and wants a paper
- User provides a research question or problem description
- User asks to review or improve an existing paper draft
- User wants to explore research ideas with literature backing

## Input Analysis

Before starting the pipeline, analyze the user's input:

### Input Type Detection

| Input Pattern | Type | Example |
|---------------|------|---------|
| Short phrase (1-5 words), no question mark | **Keyword** | "graph neural networks" |
| Question or descriptive paragraph | **Research Question** | "How can LLMs improve code review?" |
| References to a file or existing draft | **Review Mode** | "Review my draft at /path/to/file.md" |
| Mixed (topic + constraints) | **Research Question** | "Write about X using Y approach" |

### Information Extraction

From any input, extract:
1. **Core topic** - The main research area
2. **Research scope** - Specific angle or sub-problem (if any)
3. **Methodological hints** - Preferred approaches or techniques (if mentioned)
4. **Target format** - Conference paper, journal article, survey, etc.
5. **Subject field** - CS, Biology, Medicine, etc.
6. **Language** - English (default) or Chinese

## Stage 1: Research & Ideation

### Objective
Conduct a comprehensive literature survey and formulate a structured research idea.

### Step 1.1: Keyword Expansion

Expand the input topic into 5-8 related technical keywords. Consider:
- Core concepts and their variants
- Related methodologies and techniques
- Application domains
- Recent trends and emerging directions

**Strategy:** Think about what terms researchers in this field would use when searching for related work. Include both broad terms (for coverage) and specific terms (for precision).

### Step 1.2: Literature Search

Use `search_arxiv_papers` to search for papers:
- Search with the main topic first (aim for 5-10 results)
- Then search with each related keyword (aim for 2-3 results per keyword)
- Target: 15-25 papers total across all searches
- Prioritize recent papers (last 2-3 years) but include foundational works

**Search tips:**
- Use specific technical terms, not vague descriptions
- Include field qualifiers (e.g., subject_area="cs.AI")
- If initial searches return few results, try broader or alternative terms

### Step 1.3: Literature Analysis

For the most relevant 8-10 papers, extract structured information:

For each paper, document:
```
Paper: [Title]
Authors: [Authors]
Year: [Year]
Venue: [Venue/Journal]

Problem: What specific problem does this paper address?
Method: What approach/algorithm/framework does it propose?
Key Insight: What is the core innovation?
Results: What were the main findings?
Limitations: What gaps or weaknesses does the paper acknowledge or imply?
Relevance: How does this relate to our research idea? (direct/indirect/contrast)
```

### Step 1.4: Research Hypothesis Generation

Based on the literature analysis, generate 3-5 research hypotheses using:

**Inductive reasoning:** What patterns do you observe across multiple papers? What common limitations exist? What gaps are repeatedly mentioned?

**Deductive reasoning:** If a certain approach works well for problem A, could it be adapted for problem B? What would happen if we combined technique X with technique Y?

**Format each hypothesis as:**
```
Hypothesis N: [Clear, specific, testable statement]
- Basis: [What existing work supports this direction]
- Expected contribution: [What new value this would provide]
- Feasibility: [High/Medium/Low - why]
```

### Step 1.5: Research Idea Formulation

Select the most promising hypothesis and develop it into a structured research idea:

```
## Research Idea

### Problem Statement
[2-3 sentences clearly defining the problem and why it matters]

### Proposed Approach
[High-level description of the methodology, 3-5 sentences]

### Key Technical Components
1. [Component 1: what it does and why]
2. [Component 2: what it does and why]
3. [Component 3: what it does and why]

### Expected Contributions
1. [Contribution 1]
2. [Contribution 2]
3. [Contribution 3]

### Preliminary Title
[Compelling, specific title]

### Related Work Summary
[Brief summary of how this differs from existing approaches]
```

### Step 1.6: Save Output

Save the complete Stage 1 output to `/mnt/user-data/workspace/paper-draft/stage_1_ideation.md`.

## Stage 2: Literature-Driven Drafting

### Objective
Generate a complete paper draft grounded in deep literature analysis.

### Step 2.1: Technical Entity Extraction

From the Stage 1 research idea, identify 5-8 key technical entities:
- Specific algorithms or models mentioned
- Frameworks or architectures to be used/extended
- Datasets or benchmarks relevant to the problem
- Evaluation metrics or methodologies
- Theoretical concepts underlying the approach

Rank them by importance (how central they are to the proposed method).

### Step 2.2: Targeted Literature Deep-Dive

For each of the top 5-6 technical entities:
1. Use `search_arxiv_papers` to find 2-3 highly relevant papers
2. For the most important 3-5 papers, use `analyze_arxiv_paper` to get:
   - Detailed methodology description
   - Experimental setup and results
   - Innovation points and technical details
   - Comparison with other approaches

### Step 2.3: Draft Generation

Generate a complete paper draft following this structure:

#### Problem Section
- Define the research problem with sufficient context
- Explain why this problem is important and timely
- Quantify the problem's impact if possible (cite statistics from literature)
- Clearly state what gap in existing work this paper addresses

#### Rationale Section
- Explain the intuition behind the proposed approach
- Connect the approach to relevant theoretical foundations
- Discuss why existing solutions are insufficient
- Argue why the proposed approach is well-suited to the problem

#### Necessary Technical Details Section
- Describe the key algorithms, models, or frameworks
- Include mathematical formulations where appropriate
- Explain architectural choices and their justifications
- Discuss computational complexity and scalability considerations

#### Datasets Section
- List specific datasets to be used (with citations)
- Justify dataset choices (relevance, size, diversity)
- Describe any data preprocessing or augmentation needed
- Mention dataset statistics (size, number of classes, etc.) if known

#### Paper Title
- Specific, descriptive, and compelling
- Reflects the core contribution
- Follows conventions of the target venue
- Avoids overly broad or vague titles

**Title formula examples:**
- "[Method Name]: [What it does] for [Application/Problem]"
- "[Adjective] [Noun] via [Technique] for [Task]"
- "Towards [Goal]: A [Approach] Approach to [Problem]"

#### Paper Abstract
- 150-300 words
- Structure: Problem (1-2 sentences) → Gap (1 sentence) → Method (2-3 sentences) → Results (1-2 sentences) → Contribution (1 sentence)
- Be specific about the approach and expected outcomes
- Do not use undefined acronyms

#### Methods Section
- Detailed description of the proposed approach
- Include model architecture, training procedure, key components
- Reference specific techniques from the literature deep-dive
- Include mathematical notation for key equations
- Describe any novel components in detail

#### Experiments Section
- **Baselines:** List specific methods to compare against (with citations)
- **Datasets:** Reference the datasets from the Datasets section
- **Metrics:** Define evaluation metrics and why they are appropriate
- **Implementation details:** Framework, hyperparameters, hardware
- **Expected results:** What improvements are anticipated and why

**Baselines selection guidelines:**
- Include the current state-of-the-art for the task
- Include classic/baseline methods for the problem
- Include ablated versions of the proposed method
- Aim for 4-6 baselines minimum

#### Reference Section
- Numbered list format
- Only include papers that were actually found in searches
- Format: `[N]. [Authors] "[Title]" [Venue/Journal], [Year].`

### Step 2.4: Save Output

Save the complete draft to `/mnt/user-data/workspace/paper-draft/stage_2_draft.md`.

## Stage 3: Multi-Perspective Review

### Objective
Critically evaluate the draft from three independent perspectives.

### Step 3.1: Three-Dimensional Review

Review the draft independently from three perspectives. **Be critical and specific.**

#### Perspective A: Technical Feasibility (Score: 1-10)

Evaluate:
- Are the proposed methods technically sound?
- Are there obvious implementation challenges or bottlenecks?
- Are the computational requirements realistic?
- Are the assumptions reasonable?
- Are there simpler alternatives that could achieve similar results?
- Is the mathematical formulation correct and complete?
- Are there potential failure modes or edge cases?

#### Perspective B: Novelty & Significance (Score: 1-10)

Evaluate:
- Does the paper make a clear novel contribution?
- How does it compare to the closest existing work?
- Is the problem worth solving? Who would benefit?
- Would the target community find this interesting?
- Is the contribution incremental or transformative?
- Does it open new research directions?
- Is the title and abstract compelling?

#### Perspective C: Experimental Rigor (Score: 1-10)

Evaluate:
- Are the baselines appropriate, recent, and sufficient?
- Are the datasets representative and standard?
- Are the evaluation metrics well-chosen?
- Are there missing ablation studies?
- Are there missing comparisons?
- Is the experimental setup reproducible?
- Are the expected results realistic?

### Step 3.2: Review Report

For each perspective, provide:

```
## [Perspective Name] (Score: X/10)

**Strengths:**
- [Specific strength with evidence from the draft]

**Weaknesses:**
- [Specific weakness with suggestion for improvement]

**Improvement Suggestions:**
1. [Actionable suggestion with expected impact]
2. [Actionable suggestion with expected impact]
```

### Step 3.3: Optimization Plan

Synthesize the three reviews into a prioritized action plan:

```
## Optimization Plan

### Priority 1: [Most Critical Issue]
- **Issue:** [Clear description]
- **Perspective:** [Which review identified it]
- **Action:** [Specific steps to fix]
- **Literature needed:** [Keywords to search]

### Priority 2: [Second Most Critical]
...

### Priority 3: [Third Most Critical]
...

### Additional Literature Directions
- Search: [keyword 1] - to find [what]
- Search: [keyword 2] - to find [what]

### Sections Requiring Revision
- [Section name]: [Specific improvements needed]
```

### Step 3.4: Save Output

Save the review report to `/mnt/user-data/workspace/paper-draft/stage_3_review.md`.

## Stage 4: Iterative Refinement

### Objective
Address all review feedback and produce a polished final draft.

### Step 4.1: Supplementary Literature Search

For each "Literature needed" item from the optimization plan:
1. Use `search_arxiv_papers` with the suggested keywords
2. For the most relevant new papers, use `analyze_arxiv_paper`
3. Document how each new paper informs the revision

### Step 4.2: Systematic Revision

Address each priority improvement in order:

**For Priority 1 (typically a major issue):**
- May require restructuring a section or adding significant content
- Search for supporting literature before revising
- Ensure the fix doesn't introduce new problems

**For Priority 2 (typically a content gap):**
- Add missing information or comparisons
- Strengthen weak arguments with evidence
- Add missing baselines or experiments to the plan

**For Priority 3 (typically a quality improvement):**
- Improve clarity and readability
- Fix formatting or organizational issues
- Strengthen the abstract or introduction

### Step 4.3: Generate Revised Draft

Produce the complete revised draft with all improvements applied. The revised draft should:
- Follow the same format as Stage 2
- Address every weakness identified in the review
- Incorporate insights from supplementary literature
- Include updated references

### Step 4.4: Change Summary

Add a summary section documenting improvements:

```
### Summary of Changes

**Based on Technical Feasibility Review:**
- [Change 1]: [What was changed and why]

**Based on Novelty & Significance Review:**
- [Change 2]: [What was changed and why]

**Based on Experimental Rigor Review:**
- [Change 3]: [What was changed and why]

**New Literature Incorporated:**
- [Paper 1]: [How it informed the revision]
- [Paper 2]: [How it informed the revision]
```

### Step 4.5: Save Output

Save the revised draft to `/mnt/user-data/workspace/paper-draft/stage_4_revised.md`.

## Stage 5: Final Output

### Objective
Format the final draft and deliver the output.

### Step 5.1: Reference Verification

- Verify all cited papers were actually found in searches
- Ensure reference format is consistent
- Check that all in-text references have corresponding entries
- Remove any fabricated or unverified references

### Step 5.2: Quality Check

Verify the final draft:
- [ ] Title is compelling and specific
- [ ] Abstract is 150-300 words and self-contained
- [ ] Problem is clearly defined
- [ ] Methodology is described in sufficient detail
- [ ] Experimental design includes appropriate baselines
- [ ] All references are real and properly formatted
- [ ] No sections are empty or placeholder
- [ ] Logical flow between sections

### Step 5.3: Save Final Output

Save the final English draft to `/mnt/user-data/outputs/paper_draft_en.md`.

If Chinese translation was requested:
- Translate the draft preserving academic terminology
- Add English terms in parentheses for first-occurrence technical terms
- Save to `/mnt/user-data/outputs/paper_draft_zh.md`

### Step 5.4: Return Summary

Return a concise summary including:
- Paper title
- One-paragraph abstract
- Key contributions (numbered list)
- Total references cited
- File paths to saved outputs

## Quality Standards

A high-quality paper draft should:
- Have a **specific, non-trivial** problem statement
- Propose a **novel** approach (not just a combination of existing methods without justification)
- Include **concrete** experimental design with real baselines and datasets
- Cite **recent** papers (within last 2-3 years for most references)
- Have a **compelling** title that communicates the contribution
- Be **self-contained** (readable without external context)
- Demonstrate **awareness** of the field (appropriate related work coverage)

## Common Pitfalls to Avoid

- **Vague problem statements**: "X is important" without specifying what aspect or why existing solutions fail
- **Generic methods**: Proposing "deep learning" without architectural details
- **Missing baselines**: Not comparing against well-known approaches
- **Fabricated citations**: Referencing papers that were not actually found
- **Overly broad scope**: Trying to solve everything rather than focusing on a specific contribution
- **Weak experimental design**: Missing ablations, wrong metrics, insufficient baselines
- **Title mismatch**: Title doesn't reflect the actual contribution
