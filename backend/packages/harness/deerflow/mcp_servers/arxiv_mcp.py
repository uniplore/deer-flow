"""arXiv MCP Server - Provides academic paper search and retrieval capabilities."""

import asyncio
import logging
import re
import time
from typing import Any

import arxiv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arxiv-mcp-server")

# Rate limiting to avoid HTTP 429 errors
_last_request_time = 0
_min_request_interval = 10.0  # Minimum seconds between requests


def _rate_limit_delay():
    """Ensure minimum delay between arXiv API requests."""
    global _last_request_time
    current_time = time.time()
    time_since_last = current_time - _last_request_time

    if time_since_last < _min_request_interval:
        delay = _min_request_interval - time_since_last
        logger.info(f"Rate limiting: waiting {delay:.1f} seconds...")
        time.sleep(delay)

    _last_request_time = time.time()


# Create MCP server instance
server = Server("arxiv-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools provided by the arXiv MCP server."""
    return [
        Tool(
            name="search_papers",
            description="Search the arXiv database for academic papers. Returns papers with arXiv ID, title, authors, summary, DOI, published date, and URLs. Useful for finding related work, state-of-the-art papers, or papers by specific authors.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query - keywords, author name, or title fragments"
                    },
                    "subject_area": {
                        "type": "string",
                        "description": "arXiv subject area (e.g., 'cs.AI', 'physics.astro-ph', 'physics.hep-ph'). Leave empty for all areas.",
                        "optional": True
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                        "optional": True
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_paper_details",
            description="Get detailed information about a specific arXiv paper by its ID. Returns full metadata including title, authors, abstract, publication date, DOI, primary category, and all categories.",
            inputSchema={
                "type": "object",
                "properties": {
                    "arxiv_id": {
                        "type": "string",
                        "description": "arXiv paper ID (e.g., '2301.1234' or 'cs.AI/2301.1234')"
                    }
                },
                "required": ["arxiv_id"]
            }
        ),
        Tool(
            name="download_paper",
            description="Download a paper PDF from arXiv by its ID. Returns the PDF content as base64 encoded data along with metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "arxiv_id": {
                        "type": "string",
                        "description": "arXiv paper ID (e.g., '2301.1234' or 'cs.AI/2301.1234')"
                    }
                },
                "required": ["arxiv_id"]
            }
        )
    ]


async def _search_arxiv_papers(
    query: str,
    subject_area: str | None = None,
    max_results: int = 10
) -> list[dict[str, Any]]:
    """Search arXiv for papers by query and subject area.

    Args:
        query: Search query (keywords, author, title, etc.)
        subject_area: arXiv subject area (e.g., 'cs.AI', 'physics.astro-ph')
        max_results: Maximum number of results to return

    Returns:
        List of paper dictionaries with metadata
    """
    # Apply rate limiting
    _rate_limit_delay()

    # Build search query
    search_query = f"all:{query}"
    if subject_area:
        search_query += f" cat:{subject_area}"

    # Create client and search with increased delay to respect rate limits
    client = arxiv.Client(
        page_size=max_results,
        delay_seconds=10.0,  # Increased from 3.0 to avoid rate limiting
        num_retries=5,
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
            "arxiv_id": result.entry_id.split("/")[-1],
            "title": result.title,
            "authors": ", ".join([author.name for author in result.authors]),
            "summary": result.summary,
            "doi": doi,
            "published": result.published.strftime("%Y-%m-%d") if result.published else None,
            "url": result.entry_id,
            "pdf_url": f"https://arxiv.org/pdf/{result.entry_id.split('/')[-1]}.pdf",
            "primary_category": result.primary_category,
            "categories": list(result.categories),
        })

    return results


async def _get_paper_details(arxiv_id: str) -> dict[str, Any] | None:
    """Get detailed information about a specific arXiv paper.

    Args:
        arxiv_id: arXiv paper ID

    Returns:
        Dictionary with paper metadata or None if not found
    """
    try:
        # Apply rate limiting
        _rate_limit_delay()
        # Create client with increased delay to respect rate limits
        client = arxiv.Client(
            page_size=1,
            delay_seconds=10.0,  # Increased from 3.0 to avoid rate limiting
            num_retries=5,
        )

        # Build search for specific paper
        search = arxiv.Search(
            query=f"id:{arxiv_id}",
            max_results=1,
        )

        results = list(client.results(search))
        if not results:
            return None

        result = results[0]

        # Extract DOI from summary if available
        summary_text = result.summary
        doi_match = re.search(r"doi:?\s*(10\.\d{4,9}/[^\s]+)", summary_text, re.IGNORECASE)
        doi = doi_match.group(0).replace("doi:", "").replace("DOI:", "").strip() if doi_match else None

        return {
            "arxiv_id": result.entry_id.split("/")[-1],
            "title": result.title,
            "authors": ", ".join([author.name for author in result.authors]),
            "summary": result.summary,
            "doi": doi,
            "published": result.published.strftime("%Y-%m-%d") if result.published else None,
            "updated": result.updated.strftime("%Y-%m-%d") if result.updated else None,
            "url": result.entry_id,
            "pdf_url": f"https://arxiv.org/pdf/{result.entry_id.split('/')[-1]}.pdf",
            "primary_category": result.primary_category,
            "categories": list(result.categories),
            "comment": result.comment if hasattr(result, 'comment') else None,
            "journal_ref": result.journal_ref if hasattr(result, 'journal_ref') else None,
        }
    except Exception as e:
        logger.error(f"Error getting paper details: {e}")
        return None


async def _download_paper_pdf(arxiv_id: str) -> tuple[bytes | None, str | None]:
    """Download a paper PDF from arXiv.

    Args:
        arxiv_id: arXiv paper ID

    Returns:
        Tuple of (pdf_bytes, error_message)
    """
    try:
        # Apply rate limiting
        _rate_limit_delay()

        # Clean arxiv_id (remove "arXiv:" prefix if present)
        clean_id = arxiv_id.replace("arXiv:", "").replace("arxiv:", "").strip()

        # Create client with increased delay to respect rate limits
        client = arxiv.Client(
            delay_seconds=10.0,  # Increased delay to avoid rate limiting
            num_retries=5,
        )

        # Build search for specific paper
        search = arxiv.Search(
            query=f"id:{clean_id}",
            max_results=1,
        )

        results = list(client.results(search))
        if not results:
            return None, f"Paper not found: {arxiv_id}"

        result = results[0]

        # Download PDF
        pdf_bytes = result.download_pdf()
        if pdf_bytes is None:
            return None, f"Failed to download PDF for: {arxiv_id}"

        return pdf_bytes, None
    except Exception as e:
        logger.error(f"Error downloading paper: {e}")
        return None, str(e)


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls to the arXiv MCP server."""
    try:
        if name == "search_papers":
            query = arguments.get("query")
            subject_area = arguments.get("subject_area")
            max_results = arguments.get("max_results", 10)

            if not query:
                raise ValueError("Missing required parameter: query")

            results = await _search_arxiv_papers(query, subject_area, max_results)

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No papers found for query: '{query}'"
                )]

            # Format results
            output = f"## Search Results for '{query}' {'in ' + subject_area if subject_area else ''}\n\n"
            output += f"Found {len(results)} paper(s):\n\n"

            for i, paper in enumerate(results, 1):
                output += f"### {i}. {paper['title']}\n\n"
                output += f"**arXiv ID**: {paper['arxiv_id']}\n"
                output += f"**Authors**: {paper['authors']}\n"
                output += f"**Published**: {paper['published']}\n"
                output += f"**DOI**: {paper['doi'] or 'Not available'}\n"
                output += f"**URL**: {paper['url']}\n"
                output += f"**PDF**: {paper['pdf_url']}\n\n"
                output += f"**Summary**: {paper['summary'][:500]}{'...' if len(paper['summary']) > 500 else ''}\n\n"
                output += "---\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_paper_details":
            arxiv_id = arguments.get("arxiv_id")

            if not arxiv_id:
                raise ValueError("Missing required parameter: arxiv_id")

            paper = await _get_paper_details(arxiv_id)

            if not paper:
                return [TextContent(
                    type="text",
                    text=f"Paper not found: {arxiv_id}"
                )]

            # Format details
            output = f"## Paper Details: {paper['title']}\n\n"
            output += f"**arXiv ID**: {paper['arxiv_id']}\n"
            output += f"**Authors**: {paper['authors']}\n"
            output += f"**Published**: {paper['published']}\n"
            output += f"**Updated**: {paper['updated']}\n"
            output += f"**DOI**: {paper['doi'] or 'Not available'}\n"
            output += f"**URL**: {paper['url']}\n"
            output += f"**PDF**: {paper['pdf_url']}\n"
            output += f"**Primary Category**: {paper['primary_category']}\n"
            output += f"**Categories**: {', '.join(paper['categories'])}\n\n"

            if paper.get('journal_ref'):
                output += f"**Journal Reference**: {paper['journal_ref']}\n"
            if paper.get('comment'):
                output += f"**Comment**: {paper['comment']}\n"

            output += f"\n**Abstract**:\n{paper['summary']}\n"

            return [TextContent(type="text", text=output)]

        elif name == "download_paper":
            arxiv_id = arguments.get("arxiv_id")

            if not arxiv_id:
                raise ValueError("Missing required parameter: arxiv_id")

            pdf_bytes, error = await _download_paper_pdf(arxiv_id)

            if error:
                return [TextContent(
                    type="text",
                    text=f"Error downloading paper: {error}"
                )]

            # Get paper details for metadata
            paper = await _get_paper_details(arxiv_id)

            # Format response
            output = f"## Paper Downloaded: {paper['title'] if paper else arxiv_id}\n\n"
            output += f"**arXiv ID**: {arxiv_id}\n"
            output += f"**PDF Size**: {len(pdf_bytes)} bytes\n\n"

            if paper:
                output += f"**Authors**: {paper['authors']}\n"
                output += f"**Published**: {paper['published']}\n"
                output += f"**DOI**: {paper['doi'] or 'Not available'}\n"
                output += f"**Summary**: {paper['summary'][:300]}{'...' if len(paper['summary']) > 300 else ''}\n\n"

            output += "**Note**: PDF content is available in binary format. You can save it to a file for further processing."

            return [TextContent(type="text", text=output)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except ValueError as e:
        logger.error(f"Validation error in tool call: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in tool call: {e}")
        raise ValueError(f"Tool execution failed: {str(e)}")


async def main():
    """Main entry point for the arXiv MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
