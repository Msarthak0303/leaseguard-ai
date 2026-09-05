from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF lease agreement.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    reader = PdfReader(str(path))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return clean_text(
        "\n".join(pages)
    )


def extract_text_from_txt(file_path):
    """
    Extract text from a plain text lease file.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    return clean_text(
        path.read_text(
            encoding="utf-8"
        )
    )


def clean_text(text):
    """
    Basic text cleanup.
    """

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)