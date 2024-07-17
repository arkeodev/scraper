import re
from typing import Optional


class ContentDetector:
    """Base class for content format detection."""

    def detect(self, content: str) -> str:
        raise NotImplementedError(
            "Each subclass must implement its own detection method."
        )


class HTMLDetector(ContentDetector):
    def detect(self, content: str) -> str:
        if re.search(r"<html|<!DOCTYPE html>", content, re.IGNORECASE):
            return "HTML"
        return ""


class MarkdownDetector(ContentDetector):
    def detect(self, content: str) -> str:
        if re.search(r"^\s*(\#|\*|\-|\+|\d+\.)\s", content, re.MULTILINE):
            return "Markdown"
        return ""


class JSONDetector(ContentDetector):
    def detect(self, content: str) -> str:
        if re.match(r"^\s*\{.*\}\s*$", content, re.DOTALL):
            return "JSON"
        return ""


class XMLDetector(ContentDetector):
    def detect(self, content: str) -> str:
        if re.search(r"<\?xml|<\w+\s*[^>]*>", content):
            return "XML"
        return ""


class ContentFormatGuesser:
    def __init__(self):
        self.detectors = [
            HTMLDetector(),
            MarkdownDetector(),
            JSONDetector(),
            XMLDetector(),
        ]

    def guess_format(self, content: str) -> str:
        for detector in self.detectors:
            format_name = detector.detect(content)
            if format_name:
                return format_name
        return "Unknown"
