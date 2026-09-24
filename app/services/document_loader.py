from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


def load_document(path: str) -> str:
    file_path = Path(path)

    return load_document_bytes(file_path.name, file_path.read_bytes())


def load_document_bytes(filename: str, content: bytes) -> str:
    """Extract text from a supported document without persisting the upload."""
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix in {".txt", ".md"}:
        return content.decode("utf-8")

    raise ValueError(f"Unsupported file type: {suffix}")
