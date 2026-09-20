from pathlib import Path

from pypdf import PdfReader


def load_document(path: str) -> str:
    file_path = Path(path)

    if file_path.suffix.lower() == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if file_path.suffix.lower() in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8")

    raise ValueError(f"Unsupported file type: {file_path.suffix}")
