"""Built-in subagent configurations."""

from .bash_agent import BASH_AGENT_CONFIG
from .general_purpose import GENERAL_PURPOSE_CONFIG
from .paper_draft_agent import PAPER_DRAFT_AGENT_CONFIG
from .paper_summarize_agent import PAPER_SUMMARIZE_AGENT_CONFIG

__all__ = [
    "GENERAL_PURPOSE_CONFIG",
    "BASH_AGENT_CONFIG",
    "PAPER_DRAFT_AGENT_CONFIG",
    "PAPER_SUMMARIZE_AGENT_CONFIG",
]

# Registry of built-in subagents
BUILTIN_SUBAGENTS = {
    "general-purpose": GENERAL_PURPOSE_CONFIG,
    "bash": BASH_AGENT_CONFIG,
    "paper-draft-agent": PAPER_DRAFT_AGENT_CONFIG,
    "paper-summarize-agent": PAPER_SUMMARIZE_AGENT_CONFIG,
}
