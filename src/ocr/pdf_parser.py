from pathlib import Path
from typing import Iterable, Optional, Union

import logging

try:
    import pdfplumber  # type: ignore
except ImportError:  # pragma: no cover
    pdfplumber = None  # type: ignore

try:
    from PyPDF2 import PdfReader  # type: ignore
except ImportError:  # pragma: no cover
    PdfReader = None  # type: ignore

from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


class PDFParser:
    """Lightweight PDF text extractor with graceful fallbacks."""

    def __init__(self, use_pdfplumber: bool = True) -> None:
        self.use_pdfplumber = use_pdfplumber and pdfplumber is not None
        if self.use_pdfplumber:
            logger.info("Using pdfplumber backend for OCR")
        elif PdfReader is not None:
            logger.info("Using PyPDF2 backend for OCR")
        else:  # pragma: no cover - defensive branch
            raise ImportError("Either pdfplumber or PyPDF2 is required for PDF parsing")

    def extract_text(self, path: Union[str, Path]) -> str:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)

        if self.use_pdfplumber and pdfplumber is not None:
            return self._extract_with_pdfplumber(path)
        if PdfReader is None:
            raise RuntimeError("No PDF backend available")
        return self._extract_with_pypdf2(path)

    def _extract_with_pdfplumber(self, path: Path) -> str:
        with pdfplumber.open(str(path)) as pdf:
            text_chunks: Iterable[str] = (page.extract_text() or "" for page in pdf.pages)
            return "\n".join(chunk.strip() for chunk in text_chunks if chunk)

    def _extract_with_pypdf2(self, path: Path) -> str:
        assert PdfReader is not None
        reader = PdfReader(str(path))
        text_chunks = (page.extract_text() or "" for page in reader.pages)
        return "\n".join(chunk.strip() for chunk in text_chunks if chunk)
