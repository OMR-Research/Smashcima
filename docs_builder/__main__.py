import subprocess
from pathlib import Path
from typing import List, Set

from .Fragment import Fragment


def load_fragments(path_fragments: Path) -> List[Fragment]:
    """Loads fragments based on the fragmens.txt file"""
    rel_paths = path_fragments.read_text().splitlines()
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
        f.remove_ids_from_headings()


def build_html_file(
    fragments: List[Fragment],
    path_html: Path,
    title: str
):
    print("Merging fragments...")
    joined_html = "\n".join(f.export_html() for f in fragments)
    result = subprocess.run(
        [
            "pandoc", "--standalone",
            "-c", "github-markdown.css", # reference the CSS file
            "--metadata", "title=" + title,
            "-f", "html", "-t", "html",
            "-o", "-"
        ],
        cwd=str(Path(__file__).parent),
        stdout=subprocess.PIPE,
        input=joined_html.encode("utf-8")
    )
    complete_html = result.stdout.decode("utf-8")
    path_html.write_text(complete_html)


def build_pdf_file(path_html: Path, path_pdf: Path):
    print("Converting HTML to PDF...")
    
    # NOTE: pdfkit butchers fragment links and emojis... use chrome instead
    # import pdfkit
    # pdfkit.from_file(
    #     str(path_html),
    #     str(path_pdf),
    #     options={"enable-local-file-access": ""}
    # )

    CHROME_CMD = "chromium" # just "chrome" if you have chrome instead
    subprocess.run(
        [
            CHROME_CMD, "--headless",
            "--print-to-pdf=" + str(path_pdf.absolute()),
            "--no-pdf-header-footer",
            "file://" + str(path_html.absolute())
        ],
        cwd=str(Path(__file__).parent)
    )


def build_user_documentation():
    print("Building USER documentation...")
    
    f = Path(__file__).parent
    path_fragments = f / "user-docs-fragments.txt"
    path_html = f / "user-docs.html"
    path_pdf = f / "user-docs.pdf"
    
    fragments = load_fragments(path_fragments)
    process_fragments(fragments)
    build_html_file(
        fragments,
        path_html,
        "Smashcima User Documentation"
    )
    build_pdf_file(path_html, path_pdf)
    
    print("Done.")


def build_technical_documentation():
    print("Building TECHNICAL documentation...")
    
    f = Path(__file__).parent
    path_fragments = f / "technical-docs-fragments.txt"
    path_html = f / "technical-docs.html"
    path_pdf = f / "technical-docs.pdf"
    
    fragments = load_fragments(path_fragments)
    process_fragments(fragments)
    build_html_file(
        fragments,
        path_html,
        "Smashcima Technical Documentation"
    )
    build_pdf_file(path_html, path_pdf)
    
    print("Done.")


def main():
    build_user_documentation()
    print()
    
    build_technical_documentation()
    print()


# run all magic
main()
