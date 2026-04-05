"""PDF Extractor MCP Server - 提供学术论文内容提取能力。"""

import asyncio
import json
import logging
import os
import re
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdf-extractor-mcp-server")

# 创建MCP服务器实例
server = Server("pdf-extractor-mcp-server")


async def _extract_title_with_grobid(pdf_path: str) -> str | None:
    """使用GROBID服务提取论文标题。

    参数:
        pdf_path: PDF文件路径

    返回:
        论文标题，如果提取失败则返回None
    """
    try:
        from app.utils.grobid import GrobidTool

        if not os.path.exists(pdf_path):
            logger.error(f"PDF文件不存在: {pdf_path}")
            return None

        grobid_client = GrobidTool()
        title = grobid_client.extract_paper_title(pdf_path)

        if title:
            logger.info(f"成功从 {pdf_path} 提取标题")
            return title.strip()
        else:
            logger.warning(f"无法从 {pdf_path} 提取标题")
            return None

    except Exception as e:
        logger.error(f"使用GROBID提取标题时出错: {e}")
        return None


async def _extract_full_text_with_mineru(pdf_path: str) -> str | None:
    """使用MinerU提取PDF全文。

    参数:
        pdf_path: PDF文件路径

    返回:
        PDF全文，如果提取失败则返回None
    """
    try:
        # 尝试导入MinerU
        try:
            from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter
            from magic_pdf.model.sub_models.parse_doc_parse_class import ParseDocClass
            import fitz  # PyMuPDF

            if not os.path.exists(pdf_path):
                logger.error(f"PDF文件不存在: {pdf_path}")
                return None

            # 使用MinerU提取文本
            logger.info(f"使用MinerU从 {pdf_path} 提取全文")
            image_writer = DiskReaderWriter(os.path.join(os.path.dirname(pdf_path), "images"))
            pdf_bytes = open(pdf_path, "rb").read()

            # 解析PDF
            parse = ParseDocClass(pdf_bytes, image_writer, is_debug=False)
            doc_list = parse.parse_pdf()

            # 提取文本
            full_text = []
            for page in doc_list:
                if hasattr(page, 'text_blocks'):
                    for block in page.text_blocks:
                        if block:
                            full_text.append(str(block))

            if full_text:
                result = "\n".join(full_text)
                logger.info(f"成功使用MinerU从 {pdf_path} 提取全文，共 {len(result)} 字符")
                return result
            else:
                logger.warning(f"MinerU未能从 {pdf_path} 提取文本")
                return None

        except ImportError as e:
            logger.warning(f"MinerU未安装，将尝试使用PyPDF2: {e}")
            return None

    except Exception as e:
        logger.error(f"使用MinerU提取全文时出错: {e}")
        return None


async def _extract_full_text_with_pypdf2(pdf_path: str) -> str | None:
    """使用PyPDF2提取PDF全文。

    参数:
        pdf_path: PDF文件路径

    返回:
        PDF全文，如果提取失败则返回None
    """
    try:
        import PyPDF2

        if not os.path.exists(pdf_path):
            logger.error(f"PDF文件不存在: {pdf_path}")
            return None

        logger.info(f"使用PyPDF2从 {pdf_path} 提取全文")

        full_text = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    full_text.append(text)

        if full_text:
            result = "\n".join(full_text)
            logger.info(f"成功使用PyPDF2从 {pdf_path} 提取全文，共 {len(result)} 字符")
            return result
        else:
            logger.warning(f"PyPDF2未能从 {pdf_path} 提取文本")
            return None

    except Exception as e:
        logger.error(f"使用PyPDF2提取全文时出错: {e}")
        return None


def _extract_references_from_text(text: str) -> dict[str, list[str]]:
    """从文本中提取DOI和arXiv ID。

    参数:
        text: 要分析的文本

    返回:
        包含DOI和arXiv ID的字典
    """
    references = {
        "doi": [],
        "arxiv": []
    }

    # 提取DOI（匹配常见DOI格式）
    doi_pattern = r'https?://(?:dx\.)?doi\.org/([^\s]+)|(?:doi:?\s*)([0-9]+\.[0-9]+/[^\s]+)'
    doi_matches = re.findall(doi_pattern, text, re.IGNORECASE)
    for match in doi_matches:
        doi = match[0] if match[0] else match[1]
        if doi:
            references["doi"].append(doi.strip())

    # 提取arXiv ID
    arxiv_pattern = r'https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]+(?:v[0-9]+)?)|arXiv:?\s*([0-9]{4}\.[0-9]+(?:v[0-9]+)?)'
    arxiv_matches = re.findall(arxiv_pattern, text, re.IGNORECASE)
    for match in arxiv_matches:
        arxiv = match[0] if match[0] else match[1]
        if arxiv:
            references["arxiv"].append(arxiv.strip())

    return references


def _extract_sections(text: str) -> list[dict[str, Any]]:
    """从文本中提取章节结构。

    参数:
        text: 要分析的文本

    返回:
        章节列表
    """
    sections = []
    lines = text.split('\n')
    current_section = {"title": "Introduction", "content": []}
    section_pattern = r'^\d+\.?\s+[A-Z][^\n]+$|^[A-Z][A-Z\s]+$'

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检查是否是章节标题
        if re.match(section_pattern, line):
            # 保存当前章节
            if current_section["content"]:
                sections.append({
                    "title": current_section["title"],
                    "content": " ".join(current_section["content"])
                })

            # 开始新章节
            current_section = {"title": line, "content": []}
        else:
            # 添加到当前章节内容
            current_section["content"].append(line)

    # 添加最后一个章节
    if current_section["content"]:
        sections.append({
            "title": current_section["title"],
            "content": " ".join(current_section["content"])
        })

    return sections


def _extract_abstract(text: str) -> str | None:
    """从文本中提取摘要。

    参数:
        text: 要分析的文本

    返回:
        摘要文本，如果未找到则返回None
    """
    # 尝试找到Abstract部分
    abstract_patterns = [
        r'Abstract\s*:?\s*(.*?)(?:\n\n|\n\s*\n|\n(?:1\.|Introduction|Keywords))',
        r'ABSTRACT\s*:?\s*(.*?)(?:\n\n|\n\s*\n|\n(?:1\.|INTRODUCTION|KEYWORDS))',
    ]

    for pattern in abstract_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            abstract = match.group(1).strip()
            if len(abstract) > 50:  # 确保摘要有足够的内容
                logger.info(f"成功提取摘要，共 {len(abstract)} 字符")
                return abstract

    return None


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出PDF提取器MCP服务器提供的可用工具。"""
    return [
        Tool(
            name="extract_title",
            description="使用GROBID服务从PDF提取论文标题。返回标题字符串。",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "要提取标题的PDF文件路径"
                    }
                },
                "required": ["pdf_path"]
            }
        ),
        Tool(
            name="extract_full_text",
            description="使用MinerU或PyPDF2从PDF提取全文。优先使用MinerU，如果未安装则使用PyPDF2。返回PDF的完整文本内容。",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "要提取全文的PDF文件路径"
                    }
                },
                "required": ["pdf_path"]
            }
        ),
        Tool(
            name="extract_references",
            description="从PDF文本中提取引用信息，包括DOI和arXiv ID。返回包含DOI和arXiv ID列表的JSON格式数据。",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "要提取引用的PDF文件路径"
                    }
                },
                "required": ["pdf_path"]
            }
        ),
        Tool(
            name="parse_pdf",
            description="综合解析PDF，返回标题、摘要、章节结构和引用信息。包含论文的完整结构化信息。",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "要解析的PDF文件路径"
                    }
                },
                "required": ["pdf_path"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """处理对PDF提取器MCP服务器的工具调用。"""
    try:
        if name == "extract_title":
            pdf_path = arguments.get("pdf_path")

            if not pdf_path:
                raise ValueError("缺少必需参数: pdf_path")

            title = await _extract_title_with_grobid(pdf_path)

            if not title:
                return [TextContent(
                    type="text",
                    text=f"无法从 {pdf_path} 提取标题"
                )]

            return [TextContent(type="text", text=title)]

        elif name == "extract_full_text":
            pdf_path = arguments.get("pdf_path")

            if not pdf_path:
                raise ValueError("缺少必需参数: pdf_path")

            # 优先使用MinerU
            full_text = await _extract_full_text_with_mineru(pdf_path)

            # 如果MinerU失败，尝试PyPDF2
            if not full_text:
                full_text = await _extract_full_text_with_pypdf2(pdf_path)

            if not full_text:
                return [TextContent(
                    type="text",
                    text=f"无法从 {pdf_path} 提取全文"
                )]

            return [TextContent(type="text", text=full_text)]

        elif name == "extract_references":
            pdf_path = arguments.get("pdf_path")

            if not pdf_path:
                raise ValueError("缺少必需参数: pdf_path")

            # 首先提取全文
            full_text = await _extract_full_text_with_mineru(pdf_path)
            if not full_text:
                full_text = await _extract_full_text_with_pypdf2(pdf_path)

            if not full_text:
                return [TextContent(
                    type="text",
                    text=f"无法从 {pdf_path} 提取文本以获取引用"
                )]

            # 从文本中提取引用
            references = _extract_references_from_text(full_text)

            return [TextContent(
                type="text",
                text=json.dumps(references, indent=2, ensure_ascii=False)
            )]

        elif name == "parse_pdf":
            pdf_path = arguments.get("pdf_path")

            if not pdf_path:
                raise ValueError("缺少必需参数: pdf_path")

            # 验证文件存在
            if not os.path.exists(pdf_path):
                raise ValueError(f"PDF文件不存在: {pdf_path}")

            # 提取全文
            full_text = await _extract_full_text_with_mineru(pdf_path)
            if not full_text:
                full_text = await _extract_full_text_with_pypdf2(pdf_path)

            if not full_text:
                raise ValueError(f"无法从 {pdf_path} 提取文本")

            # 并行提取标题和引用
            title = await _extract_title_with_grobid(pdf_path)
            abstract = _extract_abstract(full_text)
            sections = _extract_sections(full_text)
            references = _extract_references_from_text(full_text)

            # 构建结果
            result = {
                "title": title,
                "abstract": abstract,
                "sections": sections,
                "references": references,
                "full_text": full_text
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]

        else:
            raise ValueError(f"未知工具: {name}")

    except ValueError as e:
        logger.error(f"工具调用中的验证错误: {e}")
        raise
    except Exception as e:
        logger.error(f"工具调用中的错误: {e}")
        raise ValueError(f"工具执行失败: {str(e)}")


async def main():
    """主入口点，用于PDF提取器MCP服务器。"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
