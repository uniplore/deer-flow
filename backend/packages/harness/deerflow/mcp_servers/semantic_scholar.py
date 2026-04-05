"""Semantic Scholar MCP Server - Provides academic paper search and citation analysis capabilities."""

import asyncio
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("semantic-scholar-mcp-server")

# Get API key from environment
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

# Create MCP server instance
server = Server("semantic-scholar-mcp-server")


def _format_authors(authors: list[dict[str, Any]]) -> str:
    """Format authors list to string."""
    if not authors:
        return "Unknown"
    author_names = [author.get("name", "") for author in authors if author.get("name")]
    return ", ".join(author_names) if author_names else "Unknown"


def _format_paper(paper: dict[str, Any], include_abstract: bool = True) -> str:
    """Format paper metadata to readable string."""
    output = f"**Paper ID**: {paper.get('paperId', 'N/A')}\n"
    output += f"**Title**: {paper.get('title', 'N/A')}\n"
    output += f"**Authors**: {_format_authors(paper.get('authors', []))}\n"
    output += f"**Year**: {paper.get('year', 'N/A')}\n"
    output += f"**Venue**: {paper.get('venue', 'N/A')}\n"
    output += f"**Citation Count**: {paper.get('citationCount', 0)}\n"

    if paper.get('doi'):
        output += f"**DOI**: {paper['doi']}\n"

    if paper.get('url'):
        output += f"**URL**: {paper['url']}\n"

    if include_abstract and paper.get('abstract'):
        abstract = paper['abstract']
        # Truncate abstract if too long
        if len(abstract) > 500:
            abstract = abstract[:500] + "..."
        output += f"\n**Abstract**:\n{abstract}\n"

    return output


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools provided by the Semantic Scholar MCP server."""
    return [
        Tool(
            name="search_papers",
            description="Search the Semantic Scholar database for academic papers. Returns papers with paper ID, title, authors, abstract, citation count, year, and URL. Useful for finding related work and state-of-the-art papers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query - keywords, author name, or title fragments"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                        "optional": True
                    },
                    "fields": {
                        "type": "array",
                        "description": "Fields to include in results (default: paperId, title, authors, abstract, year, citationCount, url, venue, doi)",
                        "items": {"type": "string"},
                        "default": ["paperId", "title", "authors", "abstract", "year", "citationCount", "url", "venue", "doi"],
                        "optional": True
                    },
                    "year": {
                        "type": "string",
                        "description": "Filter by publication year (e.g., '2020-2024' or '2020')",
                        "optional": True
                    },
                    "venue": {
                        "type": "string",
                        "description": "Filter by venue/conference/journal name",
                        "optional": True
                    },
                    "min_citation_count": {
                        "type": "integer",
                        "description": "Minimum citation count filter",
                        "optional": True
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_paper_details",
            description="Get detailed information about a specific Semantic Scholar paper by its ID. Returns full metadata including title, authors, abstract, publication date, DOI, venue, citation count, and reference count.",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "Semantic Scholar paper ID (e.g., '10.1145/3342101.3342103' or S2 paper ID like '2461f0b0b79c4c309b670c2a6e4f458c')"
                    },
                    "fields": {
                        "type": "array",
                        "description": "Fields to include in results (default: all common fields)",
                        "items": {"type": "string"},
                        "optional": True
                    }
                },
                "required": ["paper_id"]
            }
        ),
        Tool(
            name="get_citations",
            description="Get papers that cite the specified paper. Returns citation network information showing how the paper has been cited.",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "Semantic Scholar paper ID"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of citation results to return (default: 10)",
                        "default": 10,
                        "optional": True
                    },
                    "fields": {
                        "type": "array",
                        "description": "Fields to include in results",
                        "items": {"type": "string"},
                        "optional": True
                    }
                },
                "required": ["paper_id"]
            }
        ),
        Tool(
            name="get_references",
            description="Get papers referenced by the specified paper. Returns reference information showing what papers the paper cites.",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "Semantic Scholar paper ID"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of reference results to return (default: 10)",
                        "default": 10,
                        "optional": True
                    },
                    "fields": {
                        "type": "array",
                        "description": "Fields to include in results",
                        "items": {"type": "string"},
                        "optional": True
                    }
                },
                "required": ["paper_id"]
            }
        )
    ]


async def _search_papers(
    query: str,
    max_results: int = 10,
    fields: list[str] | None = None,
    year: str | None = None,
    venue: str | None = None,
    min_citation_count: int | None = None
) -> list[dict[str, Any]]:
    """Search Semantic Scholar for papers.

    Args:
        query: Search query
        max_results: Maximum number of results
        fields: Fields to include in results
        year: Filter by year
        venue: Filter by venue
        min_citation_count: Minimum citation
count

    Returns:
        List of paper dictionaries
    """
    try:
        import semanticscholar as scholar

        # Configure API client
        if API_KEY:
            scholar.api_key = API_KEY

        # Default fields if not specified
        if not fields:
            fields = [
                "paperId", "title", "authors", "abstract", "year",
                "citationCount", "url", "venue", "doi"
            ]

        # Build search query
        search = scholar.SearchPaper(
            query=query,
            limit=max_results,
            fields=fields,
            year=year,
            venue=venue,
            min_citation_count=min_citation_count,
        )

        # Get results
        results = list(search)
        return [paper.__dict__ if hasattr(paper, '__dict__') else paper for paper in results]

    except ImportError:
        logger.error("semanticscholar library not installed. Install with: pip install semanticscholar")
        return []
    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        return []


async def _get_paper_details(
    paper_id: str,
    fields: list[str] | None = None
) -> dict[str, Any] | None:
    """Get detailed information about a specific paper.

    Args:
        paper_id: Semantic Scholar paper ID
        fields: Fields to include in results

    Returns:
        Dictionary with paper metadata or None if not found
    """
    try:
        import semanticscholar as scholar

        # Configure API client
        if API_KEY:
            scholar.api_key = API_KEY

        # Default fields if not specified
        if not fields:
            fields = [
                "paperId", "title", "authors", "abstract", "year",
                "citationCount", "referenceCount", "url", "venue",
                "doi", "publicationDate", "publicationTypes",
                "openAccessPdf", "s2FieldsOfStudy"
            ]

        # Get paper
        paper = scholar.Paper(paper_id, fields=fields)

        if not paper:
            return None

        return paper.__dict__ if hasattr(paper, '__dict__') else paper

    except Exception as e:
        logger.error(f"Error getting paper details: {e}")
        return None


async def _get_citations(
    paper_id: str,
    max_results: int = 10,
    fields: list[str] | None = None
) -> list[dict[str, Any]]:
    """Get papers that cite the specified paper.

    Args:
        paper_id: Semantic Scholar paper ID
        max_results: Maximum number of results
        fields: Fields to include in results

    Returns:
        List of citation paper dictionaries
    """
    try:
        import semanticscholar as scholar

        # Configure API client
        if API_KEY:
            scholar.api_key = API_KEY

        # Default fields if not specified
        if not fields:
            fields = [
                "paperId", "title", "authors", "year",
                "citationCount", "url", "venue", "doi"
            ]

        # Get paper first
        paper = scholar.Paper(paper_id)
        if not paper:
            return []

        # Get citations
        citations = paper.citations(limit=max_results, fields=fields)

        return [citation.__dict__ if hasattr(citation, '__dict__') else citation for citation in citations]

    except Exception as e:
        logger.error(f"Error getting citations: {e}")
        return []


async def _get_references(
    paper_id: str,
    max_results: int = 10,
    fields: list[str] | None = None
) -> list[dict[str, Any]]:
    """Get papers referenced by the specified paper.

    Args:
        paper_id: Semantic Scholar paper ID
        max_results: Maximum number of results
        fields: Fields to include in results

    Returns:
        List of reference paper dictionaries
    """
    try:
        import semanticscholar as scholar

        # Configure API client
        if API_KEY:
            scholar.api_key = API_KEY

        # Default fields if not specified
        if not fields:
            fields = [
                "paperId", "title", "authors", "year",
                "citationCount", "url", "venue", "doi"
            ]

        # Get paper first
        paper = scholar.Paper(paper_id)
        if not paper:
            return []

        # Get references
        references = paper.references(limit=max_results, fields=fields)

        return [ref.__dict__ if hasattr(ref, '__dict__') else ref for ref in references]

    except Exception as e:
        logger.error(f"Error getting references: {e}")
        return []


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls to the Semantic Scholar MCP server."""
    try:
        if name == "search_papers":
            query = arguments.get("query")
            max_results = arguments.get("max_results", 10)
            fields = arguments.get("fields")
            year = arguments.get("year")
            venue = arguments.get("venue")
            min_citation_count = arguments.get("min_citation_count")

            if not query:
                raise ValueError("Missing required parameter: query")

            results = await _search_papers(query, max_results, fields, year, venue, min_citation_count)

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No papers found for query: '{query}'"
                )]

            # Format results
            output = f"## Search Results for '{query}'\n\n"
            if year:
                output += f"**Year Filter**: {year}\n"
            if venue:
                output += f"**Venue Filter**: {venue}\n"
            if min_citation_count:
                output += f"**Min Citation Count**: {min_citation_count}\n"
            output += f"\nFound {len(results)} paper(s):\n\n"

            for i, paper in enumerate(results, 1):
                output += f"### {i}. {paper.get('title', 'N/A')}\n\n"
                output += _format_paper(paper, include_abstract=True)
                output += "---\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_paper_details":
            paper_id = arguments.get("paper_id")
            fields = arguments.get("fields")

            if not paper_id:
                raise ValueError("Missing required parameter: paper_id")

            paper = await _get_paper_details(paper_id, fields)

            if not paper:
                return [TextContent(
                    type="text",
                    text=f"Paper not found: {paper_id}"
                )]

            # Format details
            output = "## Paper Details\n\n"
            output += _format_paper(paper, include_abstract=True)

            # Add additional metadata
            if paper.get('referenceCount'):
                output += f"**Reference Count**: {paper['referenceCount']}\n"

            if paper.get('publicationDate'):
                output += f"**Publication Date**: {paper['publicationDate']}\n"

            if paper.get('publicationTypes'):
                pub_types = ", ".join(paper['publicationTypes'])
                output += f"**Publication Types**: {pub_types}\n"

            if paper.get('openAccessPdf'):
                output += f"**Open Access PDF**: {paper['openAccessPdf']}\n"

            if paper.get('s2FieldsOfStudy'):
                fields_study = ", ".join(paper['s2FieldsOfStudy'])
                output += f"**Fields of Study**: {fields_study}\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_citations":
            paper_id = arguments.get("paper_id")
            max_results = arguments.get("max_results", 10)
            fields = arguments.get("fields")

            if not paper_id:
                raise ValueError("Missing required parameter: paper_id")

            citations = await _get_citations(paper_id, max_results, fields)

            if not citations:
                return [TextContent(
                    type="text",
                    text=f"No citations found for paper: {paper_id}"
                )]

            # Format results
            output = f"## Citations for Paper: {paper_id}\n\n"
            output += f"Found {len(citations)} paper(s) that cite this paper:\n\n"

            for i, citation in enumerate(citations, 1):
                output += f"### {i}. {citation.get('title', 'N/A')}\n\n"
                output += _format_paper(citation, include_abstract=False)
                output += "---\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_references":
            paper_id = arguments.get("paper_id")
            max_results = arguments.get("max_results", 10)
            fields = arguments.get("fields")

            if not paper_id:
                raise ValueError("Missing required parameter: paper_id")

            references = await _get_references(paper_id, max_results, fields)

            if not references:
                return [TextContent(
                    type="text",
                    text=f"No references found for paper: {paper_id}"
                )]

            # Format results
            output = f"## References for Paper: {paper_id}\n\n"
            output += f"Found {len(references)} paper(s) referenced by this paper:\n\n"

            for i, ref in enumerate(references, 1):
                output += f"### {i}. {ref.get('title', 'N/A')}\n\n"
                output += _format_paper(ref, include_abstract=False)
                output += "---\n\n"

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
    """Main entry point for the Semantic Scholar MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
