"""
pdf_to_txt_and_metadata.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Convert all PDFs in a folder to `.txt` plus a JSON lookup table.

$ pip install pdfplumber tqdm
$ python pdf_to_txt_and_metadata.py \
        --pdf-dir /Users/carsonmulligan/Desktop/Projects/Content/SurvivalGPT/RAG/pdfs \
        --txt-dir /Users/carsonmulligan/Desktop/Projects/Content/SurvivalGPT/RAG/txt
"""

import os
import json
import argparse
import pathlib
import hashlib
import pdfplumber
from tqdm import tqdm

# ---------------------------------------------------------------------------
def sha1(path: pathlib.Path, buf_size: int = 65536) -> str:
    """Cheap unique ID for each PDF (first 10 chars of SHA1)."""
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while chunk := f.read(buf_size):
            h.update(chunk)
    return h.hexdigest()[:10]

def pdf_to_txt(pdf_path: pathlib.Path, txt_path: pathlib.Path) -> dict:
    """
    Extract text, write to txt_path, and return metadata dict.
    """
    with pdfplumber.open(pdf_path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    text = "\n\n".join(pages).strip()

    txt_path.parent.mkdir(parents=True, exist_ok=True)
    txt_path.write_text(text, encoding="utf-8")

    return {
        "pdf_filename": pdf_path.name,
        "txt_filename": txt_path.name,
        "pdf_path": str(pdf_path.resolve()),
        "txt_path": str(txt_path.resolve()),
        "page_count": len(pages),
        "chars": len(text),
        "sha1_10": sha1(pdf_path),
        "snippet": text[:200] + "…" if len(text) > 200 else text
    }

# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Convert PDFs to TXT + JSON map")
    ap.add_argument("--pdf-dir", required=True, help="Folder containing PDFs")
    ap.add_argument("--txt-dir", required=True, help="Output folder for .txt files")
    ap.add_argument(
        "--out-json",
        default="pdf_text_map.json",
        help="Metadata JSON filename (default: pdf_text_map.json)",
    )
    args = ap.parse_args()

    pdf_dir = pathlib.Path(args.pdf_dir).expanduser()
    txt_dir = pathlib.Path(args.txt_dir).expanduser()
    txt_dir.mkdir(parents=True, exist_ok=True)

    meta = []

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {pdf_dir}")
        return

    for pdf_path in tqdm(pdf_files, desc="Converting PDFs"):
        txt_path = txt_dir / (pdf_path.stem + ".txt")
        try:
            meta.append(pdf_to_txt(pdf_path, txt_path))
        except Exception as e:
            print(f"✖ Error processing {pdf_path.name}: {e}")

    # write JSON
    out_path = pathlib.Path(args.out_json).expanduser()
    out_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"\n✔ All done! Metadata saved to {out_path.resolve()}")

if __name__ == "__main__":
    main()
