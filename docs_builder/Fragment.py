import subprocess
from pathlib import Path
from typing import Dict

from bs4 import BeautifulSoup, Tag


class Fragment:
    """Fragment = one markdown file, being processed"""
    def __init__(self, path: Path, soup: BeautifulSoup):
        self.path = path.absolute()
        """Absolute path to the original markdown"""

        self.soup = soup
        """DOM of the parsed HTML"""

        self.anchor_name = "docs-fragment__" + path.stem
        """hash ID of the fragment"""
    
    @staticmethod
    def load(path: Path) -> "Fragment":
        assert path.is_file()
        
        markdown = path.read_text()
        html = markdown_to_html(markdown)
        soup = BeautifulSoup(html, "html.parser")

        return Fragment(path=path, soup=soup)
    
    def insert_fragment_anchor(self):
        """Adds an anchor tag at the beginning of the fragment"""
        anchor_element = self.soup.new_tag(
            "a",
            attrs={"name": self.anchor_name}
        )
        self.soup.insert(0, anchor_element)
    
    def make_links_absolute(self):
        """Converts image and link URLs to be absolute paths"""
        absolute_fragment_dir = self.path.parent
        for img in self.soup.find_all("img"):
            if not isinstance(img, Tag): continue
            img["src"] = make_link_absolute(img["src"], absolute_fragment_dir)

        for a in self.soup.find_all("a"):
            if not isinstance(a, Tag): continue
            a["href"] = make_link_absolute(a["href"], absolute_fragment_dir)

    def convert_fragment_links_to_hash_links(
        self,
        fragments: Dict[str, "Fragment"]
    ):
        """Converts links to .md fragments pointing to their hash variants"""
        for a in self.soup.find_all("a"):
            if not isinstance(a, Tag): continue

            link = str(a.get("href", "#"))
            if not is_path_link(link): continue
            if not link.lower().endswith(".md"): continue
            
            # find the fragment in question
            fragment = fragments.get(link)
            if fragment is None:
                print("WARNING: Link to an unknown fragment:", link)
                continue

            # link that fragment's anchor ID
            a["href"] = "#" + fragment.anchor_name
    
    def remove_ids_from_headings(self):
        """Removes all ID attributes from heading tags to prevent warnings
        from duplicated element IDs"""
        for i in range(1, 7):
            for h in self.soup.find_all("h" + str(i)):
                if not isinstance(h, Tag): continue
                del h.attrs["id"]

    def export_html(self) -> str:
        return str(self.soup)


def is_path_link(link: str) -> bool:
    if not isinstance(link, str): return False
    if link.startswith("http"): return False
    if link.startswith("mailto:"): return False
    if link.startswith("#"): return False
    return True


def make_link_absolute(link: str, absolute_fragment_dir: Path) -> str:
    if not is_path_link(link):
        return link
    
    return str(Path(absolute_fragment_dir / link).absolute())


def markdown_to_html(markdown: str) -> str:
    result = subprocess.run(
        # from github-flavored md to html, output to stdout
        [
            "pandoc",
            "-f", "gfm", "-t", "html",
            "-o", "-"
        ],
        input=markdown.encode("utf-8"),
        stdout=subprocess.PIPE
    )
    return result.stdout.decode("utf-8")
