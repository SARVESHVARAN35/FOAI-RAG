import re

DEFAULT_MAX_WORDS = 500
DEFAULT_OVERLAP = 100


def split_large_section(
    text: str,
    max_words: int = DEFAULT_MAX_WORDS,
    overlap: int = DEFAULT_OVERLAP
):
    if overlap >= max_words:
        raise ValueError("overlap must be smaller than max_words")

    words = text.split()
    chunks = []

    step = max_words - overlap
    start = 0

    while start < len(words):
        end = min(start + max_words, len(words))
        chunks.append(" ".join(words[start:end]))

        if end == len(words):
            break

        start += step

    return chunks


def chunk_text(
    text: str,
    max_words: int = DEFAULT_MAX_WORDS,
    overlap: int = DEFAULT_OVERLAP
):
    text = text.strip()

    if not text:
        return []

    # ---------------------------------------------------------
    # 1. Get document title
    # ---------------------------------------------------------

    title_match = re.search(
        r"^#\s+(.+)$",
        text,
        flags=re.MULTILINE
    )

    document_title = ""

    if title_match:
        document_title = title_match.group(0).strip()

    # ---------------------------------------------------------
    # 2. Find all section headings
    # ---------------------------------------------------------

    heading_matches = list(
        re.finditer(
            r"^#{2,6}\s+.+$",
            text,
            flags=re.MULTILINE
        )
    )

    chunks = []

    # ---------------------------------------------------------
    # 3. Process each section
    # ---------------------------------------------------------

    for i, match in enumerate(heading_matches):

        heading = match.group(0).strip()

        body_start = match.end()

        # End of this section = beginning of next section
        if i + 1 < len(heading_matches):
            body_end = heading_matches[i + 1].start()
        else:
            body_end = len(text)

        body = text[body_start:body_end].strip()

        if not body:
            continue

        # -----------------------------------------------------
        # 4. Reserve words for title + heading
        # -----------------------------------------------------

        metadata_words = 0

        if document_title:
            metadata_words += len(document_title.split())

        metadata_words += len(heading.split())

        body_limit = max_words - metadata_words

        if body_limit <= 0:
            body_limit = max_words

        # -----------------------------------------------------
        # 5. Small section
        # -----------------------------------------------------

        body_words = body.split()

        if len(body_words) <= body_limit:

            parts = []

            if document_title:
                parts.append(document_title)

            parts.append(heading)
            parts.append(body)

            chunks.append("\n\n".join(parts))

            continue

        # -----------------------------------------------------
        # 6. Large section
        # -----------------------------------------------------

        body_chunks = split_large_section(
            body,
            max_words=body_limit,
            overlap=overlap
        )

        for body_chunk in body_chunks:

            parts = []

            if document_title:
                parts.append(document_title)

            parts.append(heading)
            parts.append(body_chunk)

            chunks.append("\n\n".join(parts))

    return chunks