---
name: citation-formats
description: Use whenever the user asks for citation formats, reference styles, bibliography formatting, wants to format references or citations, or needs guidance on academic citation styles. Also triggers when users ask for "APA format", "MLA citation", "IEEE reference style", "how to cite papers", or "citation guide".
---

# Citation Formats Guide

## Overview

This skill provides citation and reference formatting guidelines for academic papers. Use the appropriate format based on the target venue or field.

## In-Draft Citation Format

Within the paper draft body, use this format for referencing papers:

### Numbered Style (IEEE / Most CS Venues)

```
Recent work on graph neural networks [1, 2] has shown promising results.
Smith et al. [3] proposed a novel attention mechanism that improves...
Several studies [4-7] have explored this direction.
```

### Author-Year Style (APA / Social Sciences)

```
Recent work on graph neural networks (Smith et al., 2023; Jones, 2024) has shown promising results.
Smith et al. (2023) proposed a novel attention mechanism that improves...
Several studies (Brown, 2022; Davis & Wilson, 2023; Lee et al., 2024) have explored this direction.
```

## Reference List Formats

### IEEE Style (Computer Science - Most Common)

**Journal article:**
```
[1] A. Smith, B. Jones, and C. Lee, "Title of the Paper," IEEE Trans. Pattern Anal. Mach. Intell., vol. 45, no. 3, pp. 1234-1248, Mar. 2023.
```

**Conference paper:**
```
[2] D. Brown and E. Wilson, "Title of the Paper," in Proc. AAAI Conf. Artif. Intell. (AAAI), 2024, pp. 567-578.
```

**ArXiv preprint:**
```
[3] F. Zhang, G. Liu, and H. Wang, "Title of the Paper," 2024, arXiv:2401.12345.
```

**Book:**
```
[4] I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. Cambridge, MA, USA: MIT Press, 2016.
```

**Formatting rules:**
- Authors: Initial(s) + Last name, comma-separated. Use "et al." after 3 authors (list first author + "et al.")
- Title: In quotation marks, sentence case
- Journal/Conference: Abbreviated, italicized for journals
- Volume/Issue: vol. X, no. Y
- Pages: pp. XXX-YYY
- Year: At the end, after month if applicable

### APA 7th Edition (Social Sciences, Psychology, Education)

**Journal article:**
```
Smith, A., Jones, B., & Lee, C. (2023). Title of the paper. Journal of Machine Learning Research, 45(3), 1234-1248. https://doi.org/10.xxxx/xxxxx
```

**Conference paper:**
```
Brown, D., & Wilson, E. (2024). Title of the paper. In Proceedings of the AAAI Conference on Artificial Intelligence (pp. 567-578). AAAI Press.
```

**ArXiv preprint:**
```
Zhang, F., Liu, G., & Wang, H. (2024). Title of the paper. arXiv preprint arXiv:2401.12345.
```

**Book:**
```
Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep learning. MIT Press.
```

**Formatting rules:**
- Authors: Last name, Initial(s). Use "&" before last author. List up to 20 authors.
- Title: Sentence case, not in quotation marks
- Journal: Italicized, title case
- Year: In parentheses after authors
- DOI: Include when available as https://doi.org/...

### MLA 9th Edition (Humanities, Arts)

**Journal article:**
```
Smith, Alex, Beth Jones, and Chris Lee. "Title of the Paper." Journal of Machine Learning Research, vol. 45, no. 3, 2023, pp. 1234-1248.
```

**Conference paper:**
```
Brown, David, and Emma Wilson. "Title of the Paper." Proceedings of the AAAI Conference on Artificial Intelligence, 2024, pp. 567-578.
```

**ArXiv preprint:**
```
Zhang, Fang, Gang Liu, and Hua Wang. "Title of the Paper." arXiv, 2024, arXiv:2401.12345.
```

**Formatting rules:**
- Authors: Last name, First name. Use "et al." after 3 authors.
- Title: In quotation marks, title case
- Journal/Conference: Italicized, title case
- Year: After journal/conference info

### Chicago 17th Edition (History, Some Social Sciences)

**Author-Date system (sciences):**
```
Smith, Alex, Beth Jones, and Chris Lee. 2023. "Title of the Paper." Journal of Machine Learning Research 45, no. 3: 1234-48.
```

**Notes-Bibliography system (humanities):**
```
1. Alex Smith, Beth Jones, and Chris Lee, "Title of the Paper," Journal of Machine Learning Research 45, no. 3 (2023): 1234-48.
```

## ArXiv-Specific Citation Guidelines

When citing arXiv preprints:

1. **Always include the arXiv ID:** `arXiv:YYMM.NNNNN` (e.g., `arXiv:2401.12345`)
2. **Note submission year, not publication year** (if later published, cite the published version)
3. **Include "arXiv preprint"** in the reference entry
4. **Check if published:** Before citing an arXiv paper, check if it has been published at a venue. Prefer the published version.

**Checking for published versions:**
- Search the paper title on Google Scholar
- Check the arXiv page for "Journal reference" or "DOI" links

## Quick Reference: Choosing a Format

| Field | Recommended Format |
|-------|-------------------|
| Computer Science (AI/ML) | IEEE |
| Computer Science (Systems) | IEEE or ACM |
| Social Sciences | APA 7th |
| Humanities | MLA 9th or Chicago |
| Natural Sciences | APA 7th or IEEE |
| Engineering | IEEE |

## Common Citation Mistakes

1. **Fabricating citations**: Only cite papers you have actually found and read (or at least found via search)
2. **Wrong format**: Using APA style in an IEEE-formatted paper
3. **Missing DOIs**: Always include DOI when available
4. **Inconsistent formatting**: Mixing citation styles within the same paper
5. **Outdated references**: Citing old papers when recent work exists
6. **Self-citation excess**: Excessively citing one's own work
7. **Irrelevant citations**: Including papers that are not directly related to the work
