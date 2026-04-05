"""DBLP MCP Server - Provides computer science bibliography search capabilities."""

import asyncio
import logging
import time
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dblp-mcp-server")

# Rate limiting to avoid overwhelming DBLP servers
_last_request_time = 0
_min_request_interval = 2.0  # Minimum seconds between requests


def _rate_limit_delay():
    """Ensure minimum delay between DBLP API requests."""
    global _last_request_time
    current_time = time.time()
    time_since_last = current_time - _last_request_time

    if time_since_last < _min_request_interval:
        delay = _min_request_interval - time_since_last
        logger.info(f"Rate limiting: waiting {delay:.1f} seconds...")
        time.sleep(delay)

    _last_request_time = time.time()


# Create MCP server instance
server = Server("dblp-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools provided by DBLP MCP server."""
    return [
        Tool(
            name="search_publications",
            description="Search DBLP for computer science publications. Returns papers with DBLPMFID, title, authors, year, venue, and DOI. Useful for finding publications by author, title, or keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query - can be author name, title, or keywords"
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
            name="search_by_author",
            description="Search DBLP for publications by a specific author. Returns all publications by the author with metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "author": {
                        "type": "string",
                        "description": "Author name (format: 'Last Name, First Name' or 'First Last')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20,
                        "optional": True
                    }
                },
                "required": ["author"]
            }
        ),
        Tool(
            name="search_by_venue",
            description="Search DBLP for publications in a specific venue (conference, journal, workshop). Returns publications from that venue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "venue": {
                        "type": "string",
                        "description": "Venue name (e.g., 'NeurIPS', 'ICML', 'Nature', 'Science', 'J. ACM')"
                    },
                    "year": {
                        "type": "string",
                        "description": "Year to filter (e.g., '2023'). Leave empty for all years.",
                        "optional": True
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20,
                        "optional": True
                    }
                },
                "required": ["venue"]
            }
        ),
        Tool(
            name="get_citation_count",
            description="Get citation information for a DBLP publication by its DBLPMFID. Returns citation count and related metrics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dblp_id": {
                        "type": "string",
                        "description": "DBLP MFID (e.g., 'series/conf/nips/NIPS2017.html')"
                    }
                },
                "required": ["dblp_id"]
            }
        )
    ]


async def _search_dblp_publications(
    query: str,
    max_results: int = 10
) -> list[dict[str, Any]]:
    """Search DBLP for publications.

    Args:
        query: Search query
        max_results: Maximum number of results to return

    Returns:
        List of publication dictionaries with metadata
    """
    # Apply rate limiting
    _rate_limit_delay()

    try:
        # Use DBLP's search API (JSON endpoint)
        async with httpx.AsyncClient(timeout=30.0) as client:
            # DBLP search API (unofficial but commonly used)
            # Format: https://dblp.org/search?q={query}&format=json&h={max_results}
            url = f"https://dblp.org/search?q={query}&format=json&h={max_results}"

            response = await client.get(url)
            response.raise_for_status()

            data = response.json()

            results = []
            if "result" in data and "hits" in data["result"]:
                # Extract the 'hit' list (DBLP wraps results differently)
                hits = data["result"]["hits"]["hit"] if "hit" in data["result"]["hits"] else []

                for hit in hits[:max_results]:
                    info = hit.get("info", {})

                    # Extract authors
                    authors = []
                    if "authors" in info:
                        author_data = info["authors"].get("author", [])
                        if isinstance(author_data, dict):
                            author_data = [author_data]
                        for author in author_data:
                            if isinstance(author, dict):
                                authors.append(author.get("text", ""))
                            else:
                                authors.append(str(author))

                    # Extract DOI
                    doi = info.get("doi", {}).get("text", "") if isinstance(info.get("doi"), dict) else info.get("doi", "")

                    # Extract year from publication venue if available
                    year = info.get("year", "")

                    results.append({
                        "dblp_id": info.get("key", ""),
                        "title": info.get("title", ""),
                        "authors": ", ".join(authors) if authors else "Unknown",
                        "year": year,
                        "venue": info.get("venue", ""),
                        "doi": doi,
                        "url": f"https://dblp.org/rec/{info.get('key', '')}" if info.get('key') else "",
                        "type": info.get("type", ""),
                    })

            return results

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error searching DBLP: {e}")
        return []
    except Exception as e:
        logger.error(f"Error searching DBLP: {e}")
        return []


async def _search_by_author(
    author: str,
    max_results: int = 20
) -> list[dict[str, Any]]:
    """Search DBLP for publications by author.

    Args:
        author: Author name
        max_results: Maximum number of results to return

    Returns:
        List of publication dictionaries with metadata
    """
    # Apply rate limiting
    _rate_limit_delay()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Use author-specific search
            url = f"https://dblp.org/search/publisher?q={author}&format=json&h={max_results}"

            response = await client.get(url)
            response.raise_for_status()

            data = response.json()

            results = []
            if "result" in data and "hits" in data["result"]:
                hits = data["result"]["hits"]["hit"] if "hit" in data["result"]["hits"] else []

                for hit in hits[:max_results]:
                    info = hit.get("info", {})

                    # Extract authors
                    authors = []
                    if "authors" in info:
                        author_data = info["authors"].get("author", [])
                        if isinstance(author_data, dict):
                            author_data = [author_data]
                        for a in author_data:
                            if isinstance(a, dict):
                                authors.append(a.get("text", ""))
                            else:
                                authors.append(str(a))

                    results.append({
                        "dblp_id": info.get("key", ""),
                        "title": info.get("title", ""),
                        "authors": ", ".join(authors) if authors else "Unknown",
                        "year": info.get("year", ""),
                        "venue": info.get("venue", ""),
                        "url": f"https://dblp.org/rec/{info.get('key', '')}" if info.get('key') else "",
                    })

            return results

    except Exception as e:
        logger.error(f"Error searching by author: {e}")
        return []


async def _search_by_venue(
    venue: str,
    year: str | None = None,
    max_results: int = 20
) -> list[dict[str, Any]]:
    """Search DBLP for publications in a specific venue.

    Args:
        venue: Venue name
        year: Optional year filter
        max_results: Maximum number of results to return

    Returns:
        List of publication dictionaries with metadata
    """
    # Apply rate limiting
    _rate_limit_delay()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Build query with venue and optional year
            query = venue
            if year:
                query += f" {year}"

            url = f"https://dblp.org/search?q={query}&format=json&h={max_results}"

            response = await client.get(url)
            response.raise_for_status()

            data = response.json()

            results = []
            if "result" in data and "hits" in data["result"]:
                hits = data["result"]["hits"]["hit"] if "hit" in data["result"]["hits"] else []

                for hit in hits[:max_results]:
                    info = hit.get("info", {})

                    # Extract authors
                    authors = []
                    if "authors" in info:
                        author_data = info["authors"].get("author", [])
                        if isinstance(author_data, dict):
                            author_data = [author_data]
                        for a in author_data:
                            if isinstance(a, dict):
                                authors.append(a.get("text", ""))
                            else:
                                authors.append(str(a))

                    results.append({
                        "dblp_id": info.get("key", ""),
                        "title": info.get("title", ""),
                        "authors": ", ".join(authors) if authors else "Unknown",
                        "year": info.get("year", ""),
                        "venue": info.get("venue", ""),
                        "url": f"https://dblp.org/rec/{info.get('key', '')}" if info.get('key') else "",
                    })

            return results

    except Exception as e:
        logger.error(f"Error searching by venue: {e}")
        return []


async def _get_citation_count(dblp_id: str) -> dict[str, Any] | None:
    """Get citation information for a DBLP publication.

    Args:
        dblp_id: DBLP MFID

    Returns:
        Dictionary with citation metrics or None
    """
    # Apply rate limiting
    _rate_limit_delay()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Note: DBLP doesn't provide direct citation counts via public API
            # This is a placeholder that returns the DBLP record URL
            # In a production system, you might integrate with Semantic Scholar
            # or Google Scholar for citation counts

            url = f"https://dblp.org/rec/{dblp_id}.xml"

            response = await client.get(url)
            response.raise_for_status()

            # Parse XML for basic info
            # This is a simplified version - full parsing would use xml.etree
            return {
                "dblp_id": dblp_id,
                "url": f"https://dblp.org/rec/{dblp_id}",
                "note": "Direct citation counts not available via DBLP public API. Consider using Semantic Scholar for citation metrics.",
            }

    except Exception as e:
        logger.error(f"Error getting citation count: {e}")
        return None


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls to DBLP MCP server."""
    try:
        if name == "search_publications":
            query = arguments.get("query")
            max_results = arguments.get("max_results", 10)

            if not query:
                raise ValueError("Missing required parameter: query")

            results = await _search_dblp_publications(query, max_results)

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No publications found for query: '{query}'"
                )]

            # Format results
            output = f"## Search Results for '{query}'\n\n"
            output += f"Found {len(results)} publication(s):\n\n"

            for i, pub in enumerate(results, 1):
                output += f"### {i}. {pub['title']}\n\n"
                output += f"**DBLP ID**: {pub['dblp_id']}\n"
                output += f"**Authors**: {pub['authors']}\n"
                output += f"**Year**: {pub['year'] or 'Not specified'}\n"
                output += f"**Venue**: {pub['venue'] or 'Not specified'}\n"
                output += f"**DOI**: {pub['doi'] or 'Not available'}\n"
                output += f"**URL**: {pub['url']}\n\n"
                output += "---\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "search_by_author":
            author = arguments.get("author")
            max_results = arguments.get("max_results", 20)

            if not author:
                raise ValueError("Missing required parameter: author")

            results = await _search_by_author(author, max_results)

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No publications found for author: '{author}'"
                )]

            # Format results
            output = f"## Publications by '{author}'\n\n"
            output += f"Found {len(results)} publication(s):\n\n"

            for i, pub in enumerate(results, 1):
                output += f"### {i}. {pub['title']}\n\n"
                output += f"**DBLP ID**: {pub['dblp_id']}\n"
                output += f"**Authors**: {pub['authors']}\n"
                output += f"**Year**: {pub['year'] or 'Not specified'}\n"
                output += f"**Venue**: {pub['venue'] or 'Not specified'}\n"
                output += f"**URL**: {pub['url']}\n\n"
                output += "---\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "search_by_venue":
            venue = arguments.get("venue")
            year = arguments.get("year")
            max_results = arguments.get("max_results", 20)

            if not venue:
                raise ValueError("Missing required parameter: venue")

            results = await _search_by_venue(venue, year, max_results)

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No publications found for venue: '{venue}'"
                )]

            # Format results
            output = f"## Publications from '{venue}'"
            if year:
                output += f" ({year})"
            output += "\n\n"
            output += f"Found {len(results)} publication(s):\n\n"

            for i, pub in enumerate(results, 1):
                output += f"### {i}. {pub['title']}\n\n"
                output += f"**DBLP ID**: {pub['dblp_id']}\n"
                output += f"**Authors**: {pub['authors']}\n"
                output += f"**Year**: {pub['year'] or 'Not specified'}\n"
                output += f"**URL**: {pub['url']}\n\n"
                output += "---\n\n"

            return [TextContent(type="text", text=output)]

        elif name == "get_citation_count":
            dblp_id = arguments.get("dblp_id")

            if not dblp_id:
                raise ValueError("Missing required parameter: dblp_id")

            citation_info = await _get_citation_count(dblp_id)

            if not citation_info:
                return [TextContent(
                    type="text",
                    text=f"Unable to retrieve citation information for DBLP ID: {dblp_id}"
                )]

            # Format response
            output = f"## Citation Information\n\n"
            output += f"**DBLP ID**: {citation_info['dblp_id']}\n"
            output += f"**URL**: {citation_info['url']}\n"
            if 'note' in citation_info:
                output += f"\n{citation_info['note']}\n"

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
    """Main entry point for DBLP MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
