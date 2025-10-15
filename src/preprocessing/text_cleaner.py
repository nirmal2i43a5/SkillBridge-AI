# import re
# from typing import Iterable, Optional

# class TextCleaner:
#     EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
#     URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
#     NON_ALPHA_PATTERN = re.compile(r"[^a-zA-Z0-9\s]")

#     def __init__(self, stopwords: Optional[Iterable[str]] = None) -> None:
#         self.stopwords = set(stopwords) if stopwords else set()

#     def clean(self, text: str) -> str:
#         text = text.lower()
#         text = self.EMAIL_PATTERN.sub(" ", text)
#         text = self.URL_PATTERN.sub(" ", text)
#         text = self.NON_ALPHA_PATTERN.sub(" ", text)
#         tokens = [token for token in text.split() if token and token not in self.stopwords]
#         return " ".join(tokens)
import re
from typing import Iterable, Optional

class TextCleaner:
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
    NON_ALPHA_PATTERN = re.compile(r"[^a-zA-Z0-9\+\#\.\-/_\s]")  # preserve tech symbols

    def __init__(self, stopwords: Optional[Iterable[str]] = None) -> None:
        self.stopwords = set(stopwords) if stopwords else set()

    def clean(self, text: str) -> str:
        text = text.lower()
        text = self.EMAIL_PATTERN.sub(" ", text)
        text = self.URL_PATTERN.sub(" ", text)
        text = self.NON_ALPHA_PATTERN.sub(" ", text)
        tokens = [token for token in text.split() if token and token not in self.stopwords]
        return " ".join(tokens)

