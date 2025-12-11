from pathlib import Path
from typing import Iterable, Optional, Union
import logging
import pdfplumber 
from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


class PDFParser:
    
    def __init__(self, use_pdfplumber: bool = True) -> None:
        
        self.use_pdfplumber = use_pdfplumber and pdfplumber is not None
        
        if self.use_pdfplumber:
            logger.info("Using pdfplumber  for OCR")
        else: 
            raise ImportError("Either pdfplumber is required for PDF parsing")

    def extract_text(self, path: Union[str, Path]) -> str:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)

        if self.use_pdfplumber and pdfplumber is not None:
            return self._extract_with_pdfplumber(path)
       
        return self._extract_with_pypdf2(path)

    def _extract_with_pdfplumber(self, path: Path) -> str:
        with pdfplumber.open(str(path)) as pdf:
            text_chunks: Iterable[str] = (page.extract_text() or "" for page in pdf.pages)
            return "\n".join(chunk.strip() for chunk in text_chunks if chunk)

