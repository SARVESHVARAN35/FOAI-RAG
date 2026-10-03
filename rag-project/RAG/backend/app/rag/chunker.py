import re


def split_large_section(text: str, max_words: int = 150, overlap: int = 30):
    words = text.split()

    chunks = []
    start = 0

    while start < len(words):
        end = start + max_words
        chunk = " ".join(words[start:end])

        if chunk.strip():
            chunks.append(chunk)

        start += max_words - overlap

    return chunks


def chunk_text(text: str, max_words: int = 150, overlap: int = 30):
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        words = section.split()

        if len(words) <= max_words:
            chunks.append(section)
        else:
            section_chunks = split_large_section(
                section,
                max_words=max_words,
                overlap=overlap
            )

            chunks.extend(section_chunks)

    return chunks