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
6. **Language** - Chinese (default) or English. Only switch to English if the user explicitly requests it (e.g., "用英文写", "in English").

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

Generate a concise paper draft immediately after ideation. This is a DRAFT — keep every section focused and substantive, neither too brief nor too verbose. Use only `#` (level-1 headings).

**LANGUAGE RULE: By default, generate the entire draft in Chinese, including the title, all section headings, and body text. Only use English if the user explicitly requests it.**

**CRITICAL — REFERENCE CONSTRUCTION RULE (THIS IS THE MOST IMPORTANT RULE IN THIS DOCUMENT):**

> **The `# Reference` section MUST be constructed BY EXTRACTING citations from the body text, NOT by listing papers independently.**
>
> Follow this exact order:
> 1. First, write ALL body sections (`# Problem`, `# Rationale`, `# Related Work`, `# Technical Approach`, `# Datasets`, `# Title`, `# Abstract`, `# Methods`, `# Experiments`) with `[N](url)` in-text citations.
> 2. Then, scan every body section and collect ALL unique `[N](url)` citations that appear in the text.
> 3. Finally, build the `# Reference` list using ONLY those collected citation numbers. Each `[N]` in Reference corresponds to exactly one `[N](url)` found in the body.
>
> **NEVER add a paper to `# Reference` that does not have a matching `[N](url)` in the body.** This rule alone prevents orphan references.

**CRITICAL RULES FOR CITATIONS:**
1. **Every section (except `# Title`) MUST contain clickable in-text citations `[N](url)`.**
2. **Use `# Related Work` as the "safety net" section** — if any papers from your search have not been cited in Problem/Rationale/Methods/Experiments, you MUST cite them here. This ensures all searched papers get cited in the body.
3. **Reference is derived from body, not the other way around.** Build Reference by extracting `[N]` from the body text.

| Section | Length Guideline | Content |
|---------|-----------------|---------|
| `# Title` | One line | **Must be the FIRST section in the draft.** Specific, publication-quality title. |
| `# Problem` | 3-5 sentences | Core problem, background context, and why it matters, with clickable citations like "Recent studies [1](https://arxiv.org/abs/2401.12345), [2](url) have shown..." |
| `# Abstract` | 150-250 words | Problem, method, expected result, contribution — no filler, with key clickable citations |
| `# Related Work` | 4-8 sentences | Concise survey of closely related approaches grouped by theme. **MUST cite any papers from your search that are NOT yet cited in other sections** — this is the guaranteed citation home for all references. |
| `# Rationale` | 2-4 sentences | Why it matters, what gap it fills, limitations of existing work, with clickable citations like "Existing approaches [3](url), [4](url) suffer from..." |
| `# Technical Approach` | 4-7 sentences | Key concepts, algorithms, frameworks, and how components connect, with clickable citations like "Building on [5](url), we propose..." |
| `# Methods` | 5-8 sentences | Model architecture, training procedure, key components, loss functions, with clickable citations like "We adopt [7](url) with modifications inspired by [8](url)" |
| `# Datasets` | Bullet list | Datasets with one-line justification and clickable citations, e.g., "- ImageNet-1K [6](https://arxiv.org/abs/1409.0575): standard benchmark for..." |
| `# Experiments` | 4-7 sentences | Baselines, datasets, metrics, evaluation protocol, expected results, with clickable citations like "We compare against [9](url), [10](url) as primary baselines" |
| `# Reference` | Numbered list | **Derived from body citations.** Scan the body text, collect every `[N](url)`, and build the reference list from those numbers ONLY. **Each entry MUST be on its own line with a blank line between entries.** Format: `[N]. [Authors] "[Title]" [Venue], [Year]. arXiv:[ID] — [View Paper](url)` |

**Output order**: The draft MUST be output in the exact section order listed above — `# Title` first, `# Reference` last.

### Step 1.6: Citation Cross-Check

Before proceeding, verify citation consistency:

1. **Extract all `[N]` from the body**: Scan every section (Problem, Rationale, Related Work, Technical Approach, Datasets, Abstract, Methods, Experiments) and list all citation numbers that appear.
2. **Rebuild `# Reference` from that list**: The Reference section should contain entries ONLY for the numbers you extracted. Remove any entry whose number does not appear in the body.
3. **Format check**: Every in-text citation must be clickable `[N](url)` — NOT plain `[N]`
4. **Authenticity check**: No fabricated references — all papers must have been found via `search_arxiv_papers`
5. **Count check**: Ensure at least 6 references. If fewer, go back and add more citations to body sections (especially `# Related Work`), then rebuild Reference accordingly.

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
- Update in-text citations in body sections
- **Rebuild `# Reference` by extracting citations from the revised body text** (same procedure as Step 1.5 — Reference is always derived from body)
- Do NOT include any "Summary of Changes" section — the final draft should be clean

### Step 2.5: Citation Cross-Check

Same procedure as Step 1.6 — extract all `[N]` from the body and rebuild Reference from that list:
1. Extract all citation numbers from body sections
2. Rebuild `# Reference` to match exactly
3. Format check: all citations are clickable `[N](url)`
4. Ensure at least 6 references — if fewer, add citations to body first, then rebuild Reference

### Step 2.6: Proceed to Stage 3

Carry the revised draft and final reference list forward to Stage 3.

## Stage 3: Final Output

### Objective
Verify, format, and deliver the final draft.

### Step 3.1: Final Verification

Perform a final extraction-based verification:
1. **Extract all `[N]` from the body**: Scan every section and list all citation numbers
2. **Rebuild `# Reference` from that list**: Remove any Reference entry whose number does not appear in the body; add any missing entry for numbers that do appear
3. Verify all cited papers were actually found in searches — remove any fabricated entries
4. Ensure reference count is at least 6 — if fewer, add citations to body sections first, then rebuild Reference
5. Verify reference format: `[N]. [Authors] "[Title]" [Venue], [Year]. arXiv:[ID] — [View Paper](url)` — each entry MUST be on its own line with a blank line between entries
6. Verify every in-text citation uses clickable link format `[N](url)` — NOT plain `[N]`

**Final output must have zero orphan references — this is guaranteed by always deriving Reference from body citations.**

### Step 3.2: Quality Check

Verify the final draft:
- [ ] Uses only `#` (level-1 headings)
- [ ] Every section is concise and distilled (not a detailed exposition)
- [ ] Title is compelling and specific
- [ ] Abstract is 150-250 words
- [ ] All references are real and properly formatted (with arXiv IDs and clickable URLs)
- [ ] No sections are empty or placeholder
- [ ] Minimum 6 references
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
- **Orphan references (MOST COMMON BUG)**: Papers listed in `# Reference` but never cited in the body. **The only correct way to prevent this**: always build `# Reference` by extracting `[N]` numbers from the body text — never build Reference independently. If you find an orphan during cross-check, delete it from Reference immediately.
- **Non-clickable citations**: Using plain `[N]` instead of `[N](url)` — readers cannot click through to the paper
- **Overly broad scope**: Trying to solve everything rather than focusing on a specific contribution
- **Weak experimental design**: Missing ablations, wrong metrics, insufficient baselines
- **Title mismatch**: Title doesn't reflect the actual contribution
