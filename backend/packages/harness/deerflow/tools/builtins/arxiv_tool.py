"""arXiv literature analysis tool for thesis writer."""

import logging
from typing import Annotated, Dict, List, Optional, Tuple, Union

from langchain.tools import InjectedToolCallId, ToolRuntime, tool
from langchain_core.messages import ToolMessage

logger = logging.getLogger(__name__)


def _search_arxiv(
    query: str,
    subject_area: Optional[str] = None,
    max_results: int = 10,
) -> Union[Tuple[List[Dict], str], Tuple[None, str]]:
    """Search arXiv for papers by query and subject area.

    Args:
        query: Search query (keywords, author, title, etc.)
        subject_area: arXiv subject area (e.g., 'cs.AI', 'physics.astro-ph')
        max_results: Maximum number of results to return

    Returns:
        Tuple of (results_list, error) - one will be None
        Each result: {'id', 'title', 'authors', 'summary', 'doi', 'published', 'url', 'pdf_url'}
    """
    import re

    try:
        import arxiv

        # Build search query
        search_query = f"all:{query}"
        if subject_area:
            search_query += f" cat:{subject_area}"

        # Create client and search
        client = arxiv.Client(
            page_size=max_results,
            delay_seconds=3.0,
            num_retries=3,
        )

        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
        )

        results = []
        for result in client.results(search):
            # Extract DOI from summary if available
            summary_text = result.summary
            doi_match = re.search(r"doi:?\s*(10\.\d{4,9}/[^\s]+)", summary_text, re.IGNORECASE)
            doi = doi_match.group(0).replace("doi:", "").replace("DOI:", "").strip() if doi_match else None

            results.append({
                "id": result.entry_id.split("/")[-1],  # Extract arXiv ID
                "title": result.title,
                "authors": ", ".join([author.name for author in result.authors]),
                "summary": result.summary,
                "doi": doi,
                "published": result.published.strftime("%Y-%m-%d") if result.published else None,
                "url": result.entry_id,
                "pdf_url": f"https://arxiv.org/pdf/{result.entry_id.split('/')[-1]}.pdf",
            })

        return results, None
    except ImportError:
        return None, "arxiv library not installed. Install with: pip install arxiv"
    except Exception as e:
        return None, f"Failed to search arXiv: {str(e)}"


def _download_arxiv_paper(arxiv_id: str, output_dir: str) -> Union[Tuple[str, str], Tuple[None, str]]:
    """Download paper from arXiv by ID.

    Args:
        arxiv_id: arXiv paper ID (e.g., "2301.1234" or "cs.AI/2301.1234")
        output_dir: Directory to save downloaded files

    Returns:
        Tuple of (file_path, error) - one will be None
    """
    import os
    import requests

    # Clean arxiv_id (remove "arXiv:" prefix if present)
    clean_id = arxiv_id.replace("arXiv:", "").replace("arxiv:", "").strip()

    # Try PDF URL first
    pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
    save_path = os.path.join(output_dir, f"{clean_id.replace('/', '_')}.pdf")

    try:
        response = requests.get(pdf_url, timeout=60)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        return save_path, None
    except Exception as e:
        return None, f"Failed to download PDF: {str(e)}"


def _extract_text_from_pdf_mineru(pdf_path: str) -> Union[Tuple[str, str], Tuple[None, str]]:
    """Extract text content from PDF using MinerU.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Tuple of (extracted_text, error) - one will be None
    """
    try:
        # Try to import MinerU
        try:
            import MinerU
        except ImportError:
            # Try alternative import name
            try:
                import mineru as MinerU
            except ImportError:
                return None, "MinerU not installed. Install with: pip install mineru"

        # Use MinerU to parse PDF
        parser = MinerU(pdf_path)
        result = parser.parse()

        # Extract text from result
        if hasattr(result, "text"):
            text = result.text
        elif isinstance(result, dict) and "text" in result:
            text = result["text"]
        elif isinstance(result, str):
            text = result
        else:
            # Fallback: convert to string representation
            text = str(result)

        return text, None
    except Exception as e:
        # Fallback to PyPDF2 if MinerU fails
        try:
            import PyPDF2

            with open(pdf_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text, None
        except Exception as fallback_e:
            return None, f"Failed to extract text: MinerU error ({str(e)}), PyPDF2 fallback also failed ({str(fallback_e)})"


def _summarize_innovation_points(text: str) -> Union[Tuple[str, str], Tuple[None, str]]:
    """Summarize innovation points from paper text.

    Args:
        text: Extracted paper text

    Returns:
        Tuple of (innovation_summary, error) - one will be None
    """
    try:
        # Use a simple keyword-based extraction if no LLM available
        # In production, this would call an LLM for better summarization
        innovation_keywords = [
            "novel", "new", "innovative", "propose", "introduce", "contribution",
            "approach", "method", "framework", "architecture", "algorithm",
            "first", "state-of-the-art", "sota", "baseline", "outperform",
            "improve", "enhance", "advancement", "breakthrough"
        ]

        # Limit text to first 15000 characters for analysis
        text_content = text[:15000] if len(text) > 15000 else text

        sentences = text_content.split(". ")
        innovation_sentences = []

        for sentence in sentences[:100]:  # Analyze first 100 sentences
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in innovation_keywords):
                if len(sentence) > 20:  # Filter out very short matches
                    innovation_sentences.append(sentence.strip())

        summary = """
## Key Innovation Points

### Main Contributions:
{}

### Notable Features:
- Analyzed {} sentences containing innovation-related keywords
- Extracted from first portion of paper (more comprehensive analysis recommended)
- Consider reading full paper for complete understanding

### Suggestions for Research Proposal:
1. **Build upon these methods**: Consider how these approaches could be extended or improved
2. **Identify limitations**: The paper may mention weaknesses that could be addressed
3. **Cross-disciplinary application**: Think about applying these techniques to other domains
4. **Empirical validation**: Plan experiments to validate claims or extend benchmarks
5. **Theoretical foundations**: Deepen understanding of theoretical basis presented
""".format(
            "\n".join(f"- {s}." for s in innovation_sentences[:10]),
            len(innovation_sentences)
        )

        return summary, None
    except Exception as e:
        return None, f"Failed to summarize innovation points: {str(e)}"


@tool("search_arxiv_papers", parse_docstring=False)
def search_arxiv_tool(
    runtime: ToolRuntime,
    query: Annotated[str, "Search query (keywords, author, title, etc.)"],
    subject_area: Annotated[Optional[str], "arXiv subject area (e.g., 'cs.AI', 'physics.astro-ph'). Leave empty for all areas."] = None,
    max_results: Annotated[int, "Maximum number of results to return"] = 10,
    tool_call_id: Annotated[Optional[str], InjectedToolCallId] = None,
) -> ToolMessage:
    """Search arXiv for papers and return results with DOI information.

    Use this tool to find relevant papers for your literature review or research.

    When to use this tool:
    - Exploring related work in your research area
    - Finding state-of-the-art papers
    - Searching for papers by specific authors
    - Discovering papers in specific subject categories

    Args:
        query: Search query (keywords, author, title, etc.)
        subject_area: arXiv subject area (e.g., 'cs.AI', 'physics.astro-ph', 'physics.hep-ph')
        max_results: Maximum number of results to return

    Returns:
        List of papers with: arXiv ID, title, authors, summary, DOI, published date, and URLs
    """
    results, error = _search_arxiv(query, subject_area, max_results)
    if error:
        return ToolMessage(f"Error searching arXiv: {error}", tool_call_id=tool_call_id)

    if not results:
        return ToolMessage(f"No papers found for query: {query}", tool_call_id=tool_call_id)

    output = f"""
## Search Results for "{query}" {'in ' + subject_area + '\'' if subject_area else ''}

Found {len(results)} papers:

"""
    for i, paper in enumerate(results, 1):
        output += f"""
### {i}. {paper['title']}

**arXiv ID**: {paper['id']}
**Authors**: {paper['authors']}
**Published**: {paper['published']}
**DOI**: {paper['doi'] or 'Not available'}
**URL**: {paper['url']}
**PDF**: {paper['pdf_url']}

**Summary**:
{paper['summary'][:500]}...

---
"""

    output += f"""

**Next Steps**:
1. Use `analyze_arxiv_paper` with the arXiv ID to download and analyze specific papers
2. Example: `analyze_arxiv_paper(arxiv_id="{results[0]['id']}")`
3. The DOI information can be used for proper citation in your thesis
"""

    return ToolMessage(output, tool_call_id=tool_call_id)


@tool("analyze_arxiv_paper", parse_docstring=False)
def arxiv_tool(
    runtime: ToolRuntime,
    arxiv_id: Annotated[str, "arXiv paper ID (e.g., '2301.1234' or 'cs.AI/2301.1234')"],
    output_path: Annotated[str, "Directory to save downloaded paper and analysis"] = "/mnt/user-data/outputs",
    tool_call_id: Annotated[Optional[str], InjectedToolCallId] = None,
) -> ToolMessage:
    """Download paper from arXiv and extract innovation points for research proposal.

    This tool is designed for academic research and thesis writing. It:
    1. Downloads PDF from arXiv
    2. Extracts text content from paper using MinerU (falls back to PyPDF2)
    3. Identifies and summarizes key innovation points
    4. Provides suggestions for building a research proposal

    When to use this tool:
    - Analyzing related work for literature review
    - Identifying research gaps and opportunities
    - Gathering inspiration for methodology development
    - Understanding state-of-the-art approaches in a field

    Args:
        arxiv_id: arXiv paper ID (e.g., '2301.1234' or 'cs.AI/2301.1234')
        output_path: Directory to save downloaded paper and analysis

    Returns:
        ToolMessage with:
        - Path to downloaded PDF
        - Extracted innovation summary
        - Suggestions for research proposal
        - Error message if any step fails
    """
    import os

    try:
        # Resolve virtual path if needed
        from deerflow.config.paths import get_paths

        if runtime.state:
            thread_id = runtime.context.get("thread_id")
            if thread_id:
                thread_data = runtime.state.get("thread_data") or {}
                outputs_path = thread_data.get("outputs_path")
                if outputs_path and output_path == "/mnt/user-data/outputs":
                    output_path = outputs_path

        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Step 1: Download paper
        pdf_path, download_error = _download_arxiv_paper(arxiv_id, output_path)
        if download_error:
            return ToolMessage(f"Error downloading paper: {download_error}", tool_call_id=tool_call_id)

        # Step 2: Extract text using MinerU
        text_content, extract_error = _extract_text_from_pdf_mineru(pdf_path)
        if extract_error:
            return ToolMessage(f"Error extracting text: {extract_error}", tool_call_id=tool_call_id)

        # Step 3: Summarize innovation points
        innovation_summary, summary_error = _summarize_innovation_points(text_content)
        if summary_error:
            return ToolMessage(f"Error summarizing innovations: {summary_error}", tool_call_id=tool_call_id)

        # Step 4: Save innovation summary
        summary_path = os.path.join(output_path, f"{arxiv_id.replace('/', '_')}_innovation_analysis.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"# Innovation Analysis for arXiv:{arxiv_id}\n\n")
            f.write(f"**Paper Downloaded**: {pdf_path}\n\n")
            f.write(innovation_summary)

        result = f"""
Successfully analyzed arXiv paper: {arxiv_id}

📄 **PDF downloaded to**: {pdf_path}
📊 **Innovation analysis saved to**: {summary_path}

{innovation_summary}

**Next Steps for Your Research Proposal:**
1. Review full paper in detail using the downloaded PDF
2. Identify specific limitations or weaknesses mentioned
3. Consider how you could extend or improve upon these methods
4. Look for opportunities to apply these techniques to your research problem
5. Use the innovation points as building blocks for your methodology section

**Note**: This analysis used MinerU for PDF parsing. For more detailed analysis with AI-powered summarization,
consider using other available tools or reading the full paper manually.
"""

        return ToolMessage(result, tool_call_id=tool_call_id)

    except Exception as e:
        logger.exception("Error in arxiv_tool")
        return ToolMessage(f"Error analyzing arXiv paper: {str(e)}", tool_call_id=tool_call_id)
