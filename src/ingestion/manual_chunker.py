"""Structure-aware chunker para manuales técnicos.
Respeta secciones (§) y extrae número de página exacto.
Crítico para citar 'Manual §4.3 p.87' en la respuesta.
"""
from __future__ import annotations
import re
from pathlib import Path
import pymupdf4llm


SECTION_PATTERN = re.compile(r'^#{1,4}\s+(\d+[\.\d]*)\s+', re.MULTILINE)


def _split_on_sections(text: str, min_chars: int = 200) -> list[tuple[str, str]]:
    """Returns list of (section_id, text) tuples."""
    matches = list(SECTION_PATTERN.finditer(text))
    if not matches:
        return [("", text)]

    sections = []
    for i, m in enumerate(matches):
        section_id = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if len(content) >= min_chars:
            sections.append((section_id, content))
    return sections


def chunk_manual(pdf_path: str, max_chunk_chars: int = 1500) -> list[dict]:
    """Extrae chunks con section_id y page del manual."""
    path = Path(pdf_path)
    pages = pymupdf4llm.to_markdown(str(path), page_chunks=True)

    chunks = []
    for page_data in pages:
        page_num = page_data["metadata"]["page"]
        text = page_data["text"]

        for section_id, section_text in _split_on_sections(text):
            # Sub-chunk si la sección es muy larga
            if len(section_text) <= max_chunk_chars:
                sub_chunks = [section_text]
            else:
                # Sliding window mínimo
                step = max_chunk_chars - 100
                sub_chunks = [section_text[i: i + max_chunk_chars]
                              for i in range(0, len(section_text), step)]

            for sub in sub_chunks:
                if sub.strip():
                    chunks.append({
                        "text": sub.strip(),
                        "source": path.stem,
                        "page": page_num,
                        "section": section_id,
                        "citation": f"{path.stem} §{section_id} p.{page_num}" if section_id
                                    else f"{path.stem} p.{page_num}",
                    })
    return chunks
