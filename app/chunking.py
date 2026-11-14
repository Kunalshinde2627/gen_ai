from app.extract import load_pages
from app.fetch import PAGES, RAW_DIR, get_title
from app.records import load_records


def chunk_lines(lines, max_chars=500, overlap=1):
    """Join lines into chunks of about max_chars. The last line repeats in the next chunk."""
    chunks, current, fresh = [], [], 0
    for line in lines:
        current.append(line)
        fresh += 1
        if sum(len(x) for x in current) >= max_chars:
            chunks.append(" ".join(current))
            current = current[-overlap:] if overlap else []
            fresh = 0
    if fresh > 0 and current:
        chunks.append(" ".join(current))
    return chunks


def build_chunks():
    """Return all chunks, each with id, text, source, page and title."""
    chunks, seen = [], set()

    # 1. Real Income Tax help pages saved in data/raw
    for name, lines in load_pages().items():
        html = (RAW_DIR / f"{name}.html").read_text(encoding="utf-8")
        title = get_title(html) or name
        for number, text in enumerate(chunk_lines(lines), start=1):
            if text in seen:
                continue
            seen.add(text)
            chunks.append({
                "id": f"{name}-{number}",
                "text": text,
                "source": PAGES[name],
                "page": name,
                "title": title,
            })

    # 2. My own short records (slabs, rebate, deductions)
    for record in load_records():
        chunks.append({
            "id": record["id"],
            "text": f"{record['topic']}. {record['summary']}",
            "source": record["source_url"],
            "page": "sample_records",
            "title": record["topic"],
        })
    return chunks


if __name__ == "__main__":
    chunks = build_chunks()
    print(f"Built {len(chunks)} chunks")
    for chunk in chunks[:2] + chunks[-2:]:
        print(f"\n[{chunk['id']}] {chunk['title']} | page={chunk['page']}")
        print("  ", chunk["text"][:150])