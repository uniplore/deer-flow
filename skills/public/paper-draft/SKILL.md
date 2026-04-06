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

### Step 1.6: Proceed to Stage 2

Carry the research idea and reference list forward to Stage 2. Do not save intermediate files.

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

Generate a concise paper draft. This is a DRAFT — keep every section brief and distilled. Use only `#` (level-1 headings).

| Section | Length Guideline | Content |
|---------|-----------------|---------|
| `# Problem` | 2-3 sentences | Core problem and context |
| `# Rationale` | 1-2 sentences | Why it matters, what gap it fills |
| `# Technical Approach` | 2-4 sentences | Key concepts, algorithms, frameworks — only the essentials |
| `# Datasets` | Bullet list | Datasets with one-line justification each |
| `# Title` | One line | Specific, publication-quality title |
| `# Abstract` | 100-200 words | Problem, method, expected result, contribution — no filler |
| `# Methods` | 3-5 sentences | Model architecture, training procedure, key components — distilled |
| `# Experiments` | 2-4 sentences | Baselines, datasets, metrics, expected results — concise |
| `# Reference` | Numbered list | Only real papers found via search; format: `[N]. [Authors] "[Title]" [Venue], [Year]. arXiv:[ID]` |

### Step 2.4: Proceed to Stage 3

Carry the draft and reference list forward to Stage 3. Do not save intermediate files.

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

### Step 3.4: Proceed to Stage 4

Carry the draft, review, and reference list forward to Stage 4. Do not save intermediate files.

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
- Do NOT include any "Summary of Changes" section — the final draft should be clean

### Step 4.5: Proceed to Stage 5

Carry the revised draft and final reference list forward to Stage 5.

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
- [ ] Uses only `#` (level-1 headings)
- [ ] Every section is concise and distilled (not a detailed exposition)
- [ ] Title is compelling and specific
- [ ] Abstract is 100-200 words
- [ ] All references are real and properly formatted (with arXiv IDs)
- [ ] No sections are empty or placeholder
- [ ] Minimum 10 references


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
