import subprocess
from pathlib import Path
from typing import List, Set

import pdfkit

from .Fragment import Fragment


def load_fragments() -> List[Fragment]:
    """Loads fragments based on the fragmens.txt file"""
    rel_paths = (Path(__file__).parent / "fragments.txt").read_text() \
        .splitlines()
    repo_root = Path(__file__).parent.parent
    fragments = [
        Fragment.load(repo_root / p) for p in rel_paths
        # filter out comment lines and empties
        if not p.startswith("#") and len(p.strip()) != 0
    ]

    # check to prevent double-includes
    known_paths: Set[str] = set()
    for f in fragments:
        p = str(f.path)
        if p in known_paths:
            raise Exception(f"Fragment {p} is included twice!")
        known_paths.add(p)

    return fragments


def process_fragments(fragments: List[Fragment]):
    fragments_lookup = {
        str(f.path): f
        for f in fragments
    }

    for f in fragments:
        print(f"Processing fragment {f.path.name} ...")
        f.make_links_absolute()
        f.insert_fragment_anchor()
        f.convert_fragment_links_to_hash_links(fragments_lookup)


def build_docs_html_file(fragments: List[Fragment]):
    print("Merging fragments...")
    joined_html = "\n".join(f.export_html() for f in fragments)
    result = subprocess.run(
        [
            "pandoc", "--standalone",
            "-c", "github-markdown.css", # reference the CSS file
            "--metadata", "title=Smashcima Documentation",
            "-f", "html", "-t", "html",
            "-o", "-"
        ],
        cwd=str(Path(__file__).parent),
        stdout=subprocess.PIPE,
        input=joined_html.encode("utf-8")
    )
    complete_html = result.stdout.decode("utf-8")

    html_docs_path = Path(__file__).parent / "smashcima-docs.html"
    html_docs_path.write_text(complete_html)


def build_docs_pdf_file():
    print("Converting HTML to PDF...")
    html_docs_path = Path(__file__).parent / "smashcima-docs.html"
    pdf_docs_path = Path(__file__).parent / "smashcima-docs.pdf"
    pdfkit.from_file(
        str(html_docs_path),
        str(pdf_docs_path),
        options={"enable-local-file-access": ""}
    )


def main():
    # fragments = load_fragments()
    # process_fragments(fragments)
    # build_docs_html_file(fragments)
    build_docs_pdf_file()

    print("Done.")
    print()

    print("/!\\ NOTICE:")
    print("pdfkit package produces PDF, but it butchers fragment links...")
    print("Open the HTML file in web browser and do 'print-to-pdf' instead.")
    print("(disable headers and footers in the printing to get just the content)")


# run all magic
main()
