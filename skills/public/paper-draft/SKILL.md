---
name: paper-draft
description: Use this skill when generating, drafting, or reviewing academic research papers. Triggers on "generate paper", "write research paper", "draft academic paper", "review paper draft", "improve paper", "research idea", "create paper draft", or any academic writing task that involves literature-backed content generation.
---

# Paper Draft Generation Skill

## Overview

This skill provides a streamlined 3-stage pipeline for generating high-quality academic research paper drafts. It combines real-time literature retrieval with structured ideation and self-review to produce publication-ready drafts efficiently.


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

## Stage 1: Research, Ideation & Drafting

### Objective
Conduct literature survey, formulate research idea, and generate a complete paper draft in one pass.

### Step 1.1: Keyword Expansion

Expand the input topic into 5-8 related technical keywords. Consider:
- Core concepts and their variants
- Related methodologies and techniques
- Application domains
- Recent trends and emerging directions

### Step 1.2: Literature Search

Use `search_arxiv_papers` to search for papers — launch ALL keyword searches in parallel:
- Search with the main topic first (aim for 5-10 results)
- Then search with each related keyword (aim for 2-3 results per keyword)
- Target: 15-25 papers total across all searches
- Prioritize recent papers (last 2-3 years) but include foundational works

**Search tips:**
- Use specific technical terms, not vague descriptions
- Include field qualifiers (e.g., subject_area="cs.AI")
- If initial searches return few results, try broader or alternative terms

### Step 1.3: Literature Analysis

Use `analyze_arxiv_paper` on the 4-5 most relevant papers to get detailed content (methods, experiments, innovations).

For each analyzed paper, document:
```
Paper: [Title]
Authors: [Authors]
Year: [Year]
Venue: [Venue/Journal]
arXiv ID: [ID]

Problem: What specific problem does this paper address?
Method: What approach/algorithm/framework does it propose?
Key Insight: What is the core innovation?
Results: What were the main findings?
Limitations: What gaps or weaknesses does the paper acknowledge or imply?
Relevance: How does this relate to our research idea? (direct/indirect/contrast)
```

For remaining papers (not deeply analyzed), record: authors, title, year, venue, arXiv ID, and URL.

**IMPORTANT: Record the URL for every paper** — use the arXiv abs page URL (`https://arxiv.org/abs/YYMM.NNNNN`), DOI link (`https://doi.org/...`), or publisher page. This URL is needed for clickable in-text citations.

### Step 1.4: Research Idea Formulation

Based on the literature analysis:

1. Generate 3-5 research hypotheses grounded in the literature
2. Select the most promising hypothesis
3. Develop it into a structured research idea:

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
```

### Step 1.5: Draft Generation

Generate a concise paper draft immediately after ideation. This is a DRAFT — keep every section brief and distilled. Use only `#` (level-1 headings).

**CRITICAL RULES FOR CITATIONS:**
1. **Every section (except `# Title`) MUST contain clickable in-text citations `[N](url)`.**
2. **Every paper in the Reference list MUST be cited at least once in the body.** Do NOT add papers to Reference that you don't cite in the text.
3. **Use `# Related Work` as the "safety net" section** — if any papers from your search have not been cited in Problem/Rationale/Methods/Experiments, you MUST cite them here. This ensures zero orphan references.

| Section | Length Guideline | Content |
|---------|-----------------|---------|
| `# Problem` | 2-3 sentences | Core problem and context, with clickable citations like "Recent studies [1](https://arxiv.org/abs/2401.12345), [2](url) have shown..." |
| `# Rationale` | 1-2 sentences | Why it matters, what gap it fills, with clickable citations like "Existing approaches [3](url), [4](url) suffer from..." |
| `# Related Work` | 2-4 sentences | Brief survey of closely related approaches. **MUST cite any papers from your search that are NOT yet cited in other sections** — this is the guaranteed citation home for all references. |
| `# Technical Approach` | 2-4 sentences | Key concepts, algorithms, frameworks, with clickable citations like "Building on [5](url), we propose..." |
| `# Datasets` | Bullet list | Datasets with one-line justification and clickable citations, e.g., "- ImageNet-1K [6](https://arxiv.org/abs/1409.0575): standard benchmark for..." |
| `# Title` | One line | Specific, publication-quality title |
| `# Abstract` | 100-200 words | Problem, method, expected result, contribution — no filler, with key clickable citations |
| `# Methods` | 3-5 sentences | Model architecture, training procedure, key components, with clickable citations like "We adopt [7](url) with modifications inspired by [8](url)" |
| `# Experiments` | 2-4 sentences | Baselines, datasets, metrics, expected results, with clickable citations like "We compare against [9](url), [10](url) as primary baselines" |
| `# Reference` | Numbered list | **ONLY include papers that are cited in the body.** Format: `[N]. [Authors] "[Title]" [Venue], [Year]. arXiv:[ID] — [View Paper](url)` |

### Step 1.6: Citation Cross-Check

Before proceeding, perform a **bidirectional cross-check** and **fix any mismatches immediately**:

1. **Forward check**: For every `[N](url)` in the body, verify it has a matching `[N]` entry in `# Reference`. If missing, add it.
2. **Backward check**: For every `[N]` entry in `# Reference`, verify it appears as `[N](url)` in the body. **If an entry has NO in-text citation, do ONE of the following:**
   - If the paper is relevant to the research topic, add a citation to the most appropriate section (Problem, Rationale, Related Work, Methods, or Experiments)
   - If the paper is not relevant enough to cite in the body, **remove it from `# Reference` entirely** — do NOT keep uncited entries in the reference list
3. **Format check**: Every in-text citation must be clickable `[N](url)` — NOT plain `[N]`
4. **Authenticity check**: No fabricated references — all papers must have been found via `search_arxiv_papers`

**Rule: `# Reference` and the body must be in perfect 1:1 correspondence — no orphans in either direction.**

### Step 1.7: Proceed to Stage 2

Carry the draft and reference list forward to Stage 2. Do not save intermediate files.

## Stage 2: Self-Review & Refinement

### Objective
Critically evaluate the draft and address weaknesses with targeted improvements.

### Step 2.1: Three-Dimensional Self-Review

Review the draft independently from three perspectives. **Be critical and specific.**

#### Perspective A: Technical Feasibility (Score: 1-10)

Evaluate:
- Are the proposed methods technically sound?
- Are there obvious implementation challenges or bottlenecks?
- Are the assumptions reasonable?
- Are there simpler alternatives that could achieve similar results?

#### Perspective B: Novelty & Significance (Score: 1-10)

Evaluate:
- Does the paper make a clear novel contribution?
- How does it compare to the closest existing work?
- Is the contribution incremental or transformative?

#### Perspective C: Experimental Rigor (Score: 1-10)

Evaluate:
- Are the baselines appropriate, recent, and sufficient?
- Are the datasets representative and standard?
- Are the evaluation metrics well-chosen?
- Are there missing ablation studies or comparisons?

### Step 2.2: Gap Identification

From the review, identify specific, actionable weaknesses:
- Missing baselines or related work that should be cited
- Weak or vague methodology descriptions
- Insufficient experimental design
- Uncited important papers

### Step 2.3: Conditional Supplementary Search

**Only search if the review reveals significant gaps.** If the draft is already strong, skip to Step 2.4.

If gaps are found:
1. Use `search_arxiv_papers` with 1-3 targeted keywords to fill specific gaps (NOT a broad re-survey)
2. Use `analyze_arxiv_paper` only if a newly found paper is directly relevant to the proposed method
3. Add newly found papers to the reference list

### Step 2.4: Generate Revised Draft

Produce the complete revised draft addressing all identified weaknesses:
- Follow the same format as Stage 1
- Address every weakness identified in the review
- Incorporate insights from supplementary literature (if searched)
- Update in-text citations and reference list
- Do NOT include any "Summary of Changes" section — the final draft should be clean

### Step 2.5: Citation Cross-Check

Same procedure as Step 1.6 — perform bidirectional cross-check and **fix mismatches immediately**:
1. Forward check: every body citation has a Reference entry
2. Backward check: every Reference entry is cited in the body — if not, either add an in-text citation or remove the entry
3. Format check: all citations are clickable `[N](url)`
4. Ensure at least 10 references, each with a clickable URL

### Step 2.6: Proceed to Stage 3

Carry the revised draft and final reference list forward to Stage 3.

## Stage 3: Final Output

### Objective
Verify, format, and deliver the final draft.

### Step 3.1: Final Verification

Perform bidirectional cross-check and **fix any remaining mismatches**:
1. **Forward check**: every `[N](url)` in the body has a matching Reference entry — if missing, add it
2. **Backward check**: every Reference entry is cited in the body — if not, either add an in-text citation in the most appropriate section or **remove the uncited entry from Reference**
3. Verify all cited papers were actually found in searches — remove any fabricated entries
4. Ensure reference count is at least 10 — if fewer, search for more and add them
5. Verify reference format: `[N]. [Authors] "[Title]" [Venue], [Year]. arXiv:[ID] — [View Paper](url)`
6. Verify every in-text citation uses clickable link format `[N](url)` — NOT plain `[N]`

**Final output must have zero orphan references and zero missing reference entries.**

### Step 3.2: Quality Check

Verify the final draft:
- [ ] Uses only `#` (level-1 headings)
- [ ] Every section is concise and distilled (not a detailed exposition)
- [ ] Title is compelling and specific
- [ ] Abstract is 100-200 words
- [ ] All references are real and properly formatted (with arXiv IDs and clickable URLs)
- [ ] No sections are empty or placeholder
- [ ] Minimum 10 references
- [ ] **Zero orphan references**: every Reference entry is cited at least once in the body
- [ ] **Zero dangling citations**: every in-text `[N](url)` has a matching Reference entry
- [ ] Every in-text citation uses `[N](url)` clickable link format (NOT plain `[N]`)


## Quality Standards

A high-quality paper draft should:
- Have a **specific, non-trivial** problem statement
- Propose a **novel** approach (not just a combination of existing methods without justification)
- Include **concrete** experimental design with real baselines and datasets
- Cite **recent** papers (within last 2-3 years for most references)
- Have a **compelling** title that communicates the contribution
- Be **self-contained** (readable without external context)
- Demonstrate **awareness** of the field (appropriate related work coverage)
- Have **clickable in-text citations in every section** — every `[N]` must be a markdown link `[N](url)` to the paper page

## Common Pitfalls to Avoid

- **Vague problem statements**: "X is important" without specifying what aspect or why existing solutions fail
- **Generic methods**: Proposing "deep learning" without architectural details
- **Missing baselines**: Not comparing against well-known approaches
- **Fabricated citations**: Referencing papers that were not actually found
- **Orphan references (MOST COMMON BUG)**: Papers listed in `# Reference` but never cited in the body. **Fix**: either add an in-text citation in the appropriate section (use `# Related Work` as the safety net), or remove the entry from Reference entirely. Never leave a Reference entry uncited.
- **Non-clickable citations**: Using plain `[N]` instead of `[N](url)` — readers cannot click through to the paper
- **Overly broad scope**: Trying to solve everything rather than focusing on a specific contribution
- **Weak experimental design**: Missing ablations, wrong metrics, insufficient baselines
- **Title mismatch**: Title doesn't reflect the actual contribution
