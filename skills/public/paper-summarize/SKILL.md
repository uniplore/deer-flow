---
name: paper-summarize
description: Use this skill when reading, analyzing, or summarizing academic papers. Triggers on "read paper", "summarize paper", "analyze paper", "explain paper", "what is this paper about", "paper review", or when a user uploads/references a paper and wants to understand it. Supports both full summary mode and question-driven analysis mode.
---

# Paper Summarization Skill

## Overview

This skill provides systematic methodologies for analyzing academic papers. It supports two modes: a **default full summary flow** for comprehensive paper understanding, and a **question-driven flow** for targeted analysis based on user questions.

## When to Use This Skill

- User uploads or references a paper and wants a summary
- User asks specific questions about a paper's methodology, results, or contributions
- User wants to compare a paper's approach with alternatives
- User needs a paper explained in simpler or different-language terms
- User wants to extract key information (datasets, baselines, innovations) from a paper

## Mode Selection

| User Input | Mode | Action |
|------------|------|--------|
| "Summarize this paper" / No question | **Default Summary** | Full structured summary of all sections |
| "What method does this paper use?" | **Question-Driven** | Targeted analysis focused on methodology |
| "Explain the experiments and limitations" | **Question-Driven** | Multi-question targeted analysis |
| "Explain this paper simply" | **Default Summary** (simplified) | Full summary with simplified language |
| Upload file + "Read this" | **Default Summary** | Full structured summary |

## Default Summary Flow

### Step 1: Paper Acquisition

Determine the best way to access the paper content:

| Source Type | Action | Tool |
|-------------|--------|------|
| arXiv ID (e.g., "2401.12345") | Download and parse PDF via MinerU | `analyze_arxiv_paper` |
| Paper title | Search arXiv, then analyze via MinerU | `search_arxiv_papers` → `analyze_arxiv_paper` |
| Uploaded PDF file | Parse PDF via MinerU | `parse_pdf` |
| Uploaded markdown file | Read directly | `read_file` |
| URL (PDF link) | Download, then parse via MinerU | `bash` (download) → `parse_pdf` |
| URL (HTML page) | Fetch content | `web_fetch` |
| Already in context | Analyze directly | None |

**IMPORTANT: Always use MinerU-based parsing for PDF files.**

MinerU (`parse_pdf` / `analyze_arxiv_paper`) properly handles:
- Multi-column layouts (common in 2-column academic papers)
- Mathematical formulas and equations
- Tables with structured data
- Figure captions and references
- Header/footer removal

Plain `read_file` on a PDF will only get raw text, missing formulas, mangling table data, and mixing columns. **Never use `read_file` on PDF files — always use `parse_pdf`.**

**Workflow for uploaded PDFs:**
1. Check `/mnt/user-data/uploads/` for the uploaded PDF file
2. Use `parse_pdf(pdf_path)` to extract full structured content via MinerU
3. The parsed output includes clean markdown with formulas, tables, and section structure
4. Proceed to Step 2 with the parsed content

### Step 2: Section Identification

Scan the paper and identify its structural sections. Most papers follow this general structure:

```
Abstract → Introduction → Related Work → Methodology → Experiments → Results → Discussion → Conclusion → References
```

Map the paper's actual sections to these 5 analysis categories:

| Category | Typically Covers |
|----------|-----------------|
| **Research Background** | Abstract, Introduction, Related Work, Motivation |
| **Methodology** | Method, Approach, Model, Architecture, Algorithm, Framework |
| **Experiments** | Experiments, Results, Ablation Studies, Comparisons |
| **Dataset** | Datasets, Data Preprocessing, Benchmarks, Data Statistics |
| **Discussion** | Discussion, Conclusion, Limitations, Future Work |

### Step 3: Section-wise Analysis

For each category, extract the key information following these guidelines:

#### Research Background (3-4 sentences)
- What is the core problem this paper addresses?
- Why is this problem important? (motivation, real-world impact)
- What are the limitations of existing approaches? (research gap)
- What is the paper's high-level approach to solving this problem?

#### Methodology (detailed)
- What is the proposed method/approach called?
- Describe the overall architecture or pipeline
- What are the key components/modules? (list each with a 1-2 sentence description)
- What is the core innovation? What makes this different from prior work?
- Are there important formulas, algorithms, or theoretical foundations?
- What are the design choices and their justifications?

**Guidelines for methodology extraction:**
- Preserve technical terminology (don't replace "attention mechanism" with "focus system")
- Describe the workflow/pipeline in order
- Note any novel combinations of existing techniques
- Include loss functions, training strategies if mentioned

#### Experiments (specific and quantitative)
- What datasets were used? (names, sizes, domains)
- What baselines/methods were compared against? (list each)
- What evaluation metrics were used?
- What were the main results? (include specific numbers/percentages)
- Was there an ablation study? What did it show?
- What were the key observations from the experiments?

**Guidelines for experiment extraction:**
- Always include specific numbers (e.g., "achieved 95.3% accuracy", "reduced error by 12%")
- Note which baselines the proposed method outperforms
- Highlight any surprising or counter-intuitive findings
- Note any statistical significance tests

#### Dataset (factual)
- Dataset names and versions
- Size statistics (number of samples, classes, features)
- Domain/task type
- Any data augmentation or preprocessing applied
- Train/validation/test splits
- Whether datasets are public or proprietary

#### Discussion (evaluative)
- What are the main conclusions?
- What are the stated limitations?
- What future work is suggested?
- What is the overall significance of this work?
- Are there any potential ethical concerns or societal impact?

### Step 4: Summary Generation

Combine all section analyses into a structured markdown document following the output format in the agent's system prompt. Ensure:

- Each section is self-contained and readable independently
- Technical terms are preserved and used correctly
- Specific numbers and findings are included
- The summary is concise but comprehensive
- Key contributions are clearly highlighted

### Step 5: Reference Extraction

Extract the most important references from the paper:
- Papers that the proposed method builds upon (foundational work)
- Key baselines compared in experiments
- Seminal works in the same area

Format as a numbered list with titles and authors.

## Question-Driven Flow

### Step 1: Question Classification

Classify each user question to determine the reading strategy:

| Question Type | Focus Sections | Reading Strategy |
|---------------|---------------|-----------------|
| **Content** ("What method...") | Methodology | Deep read of method section |
| **Evaluation** ("How good are results?") | Experiments | Deep read of experiments + results |
| **Comparison** ("How does this compare to X?") | Related Work + Experiments | Cross-reference multiple sections |
| **Explanation** ("Explain the architecture") | Methodology | Detailed technical reading |
| **Critical** ("What are limitations?") | Discussion + Experiments | Analytical reading with critique |
| **Reproducibility** ("Can I reproduce this?") | Methodology + Experiments | Focus on implementation details |
| **Novelty** ("What's new here?") | Methodology + Related Work | Comparative analysis |

### Step 2: Targeted Reading

Read the paper focusing on sections relevant to the user's questions. For multiple questions, read the paper once but annotate information relevant to each question.

### Step 3: Structured Response

Address each question directly and specifically:

```
## Summary Overview
[1-2 paragraph overview for context]

## Answers to Your Questions

### Q1: [User's Question]
[Direct answer with evidence from the paper]
- Key finding: [specific detail]
- Evidence: [section/figure/table reference]

### Q2: [User's Question]
[Direct answer with evidence from the paper]

## Key Insights
[Additional observations the user might find valuable]
```

### Step 4: Proactive Insights

After answering the user's questions, provide additional insights they might not have thought to ask:
- Connections to other recent work
- Potential applications beyond what the paper discusses
- Comparison with the user's possible use case (if inferable from context)
- Practical considerations for applying this work

## Handling Special Cases

### Very Long Papers (>20 pages)
- Prioritize: Abstract → Methodology → Experiments → Discussion
- Skim: Related Work (unless specifically asked about)
- Use chunked reading for very long sections
- Focus on tables and figures for experimental results

### Papers in Non-English Languages
- Summarize in the user's preferred language
- Preserve original technical terms in parentheses
- Note if translation may affect precision

### Papers with Missing Sections
- If no experiments: focus on theoretical contributions
- If no methodology detail: note this as a limitation
- If no datasets: describe the evaluation approach used instead
- Always be transparent about what information is missing

### Survey/Review Papers
- Adjust the framework: focus on the paper's organizational structure
- Extract the taxonomy/classification the survey provides
- Summarize key findings across covered papers
- Note the survey's scope and what it does NOT cover

### Short Papers / Letters (4 pages or less)
- Provide a more detailed summary (less content to cover)
- Focus on the core contribution and key results
- May combine sections for brevity

## Quality Standards

A good paper summary should:
- Be **accurate** — all claims backed by the paper's content
- Be **specific** — include numbers, method names, dataset names
- Be **structured** — follow a consistent format
- Be **balanced** — cover strengths and limitations
- Be **autonomous** — the reader can understand the paper without reading the original
- Be **concise** — informative without being excessively long

## Common Mistakes to Avoid

- **Hallucinating content** — only describe what is actually in the paper
- **Omitting numbers** — "improved performance" is less useful than "improved accuracy from 85.2% to 91.7%"
- **Missing the novelty** — always identify what is new vs. what is standard/known
- **Over-summarizing** — losing important technical details in pursuit of brevity
- **Under-summarizing** — providing too much detail, making the summary as long as the paper
- **Ignoring limitations** — every paper has weaknesses; identify them
- **Wrong emphasis** — spending equal time on minor and major contributions
