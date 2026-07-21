"""Language-aware source parsers (Phase 2B)."""

from app.parsers.base import ParsedBlock, Parser
from app.parsers.registry import get_parser

__all__ = ["ParsedBlock", "Parser", "get_parser"]
