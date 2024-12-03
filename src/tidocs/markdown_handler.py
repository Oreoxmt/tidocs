import re
from datetime import date, datetime
from typing import Optional, Union
import yaml


def generate_pandoc_metadata(
    title: Optional[str] = None,
    author: Union[str, list[str], None] = None,
    publication_date: Union[str, date, datetime, None] = None,
    abstract: Optional[str] = None,
    toc_title: Optional[str] = None,
) -> str:
    """
    Generate a YAML metadata block for Pandoc documents.

    Args:
        title: Document title
        author: Single author or multiple authors (comma-separated string or list)
        publication_date: Date in any format or datetime object
        abstract: Document abstract
        toc_title: Title for table of contents

    Returns:
        str: Formatted YAML metadata block

    Examples:
        >>> generate_pandoc_metadata()
        '\\n---\\n\\n---\\n'
        >>> generate_pandoc_metadata(title="Sample Document")
        '\\n---\\n"title": |-\\n  Sample Document\\n\\n---\\n'
        >>> generate_pandoc_metadata(author="John Doe")
        '\\n---\\n"author": |-\\n  John Doe\\n\\n---\\n'
        >>> from datetime import date
        >>> generate_pandoc_metadata(publication_date=date(2024, 1, 1))
        '\\n---\\n"date": |-\\n  20240101\\n\\n---\\n'
        >>> generate_pandoc_metadata(abstract="This is a sample abstract\\n\\nA new line.")
        '\\n---\\n"abstract": |-\\n  This is a sample abstract\\n\\n  A new line.\\n\\n---\\n'
    """
    metadata = {}

    # Handle title
    if title:
        metadata["title"] = title

    # Handle author(s)
    if author:
        if isinstance(author, str):
            # Split string by comma and strip whitespace
            authors = [a.strip() for a in author.split(",")]
            metadata["author"] = authors if len(authors) > 1 else authors[0]
        elif isinstance(author, list):
            metadata["author"] = author if len(author) > 1 else author[0]
        else:
            metadata["author"] = str(author)

    # Handle date
    if publication_date:
        if isinstance(publication_date, (datetime, date)):
            metadata["date"] = publication_date.strftime("%Y%m%d")
        else:
            metadata["date"] = str(publication_date)

    # Handle abstract
    if abstract:
        metadata["abstract"] = abstract

    # Handle toc_title
    if toc_title:
        metadata["toc-title"] = toc_title

    if not metadata:
        yaml_str = ""
    else:
        yaml_str = yaml.dump(
            metadata,
            sort_keys=False,
            allow_unicode=True,
            width=float("inf"),
            default_style="|",
        )
    result = "\n---\n" + yaml_str + "\n---\n"
    return result


def remove_front_matter(content: bytes) -> bytes:
    """Remove YAML front matter from document content.

    Examples:
        >>> remove_front_matter(b"---\\ntitle:Test\\nsummary:Test\\n---\\nLine")
        b'Line'
        >>> remove_front_matter(b"Test\\n---\\ntitle:Test\\nsummary:Test\\n---\\nLine")
        b'Test\\nLine'
    """
    front_matter = b"---\n"

    start_index = content.find(front_matter)
    if start_index == -1:
        return content

    end_index = content.find(front_matter, start_index + len(front_matter))
    if end_index == -1:
        return content

    return content[:start_index] + content[end_index + len(front_matter) :]


def process_internal_links(content: str, base_url: str) -> str:
    """Process internal links to include base URL.

    Examples:
        >>> process_internal_links("[Test](/test1/test2/a.md#b)", "https://www.test.com/v1")
        '[Test](https://www.test.com/v1/a#b)'
        >>> process_internal_links("[Test](/test1/test2/a.md#b)", "https://www.test.com/v1/")
        '[Test](https://www.test.com/v1/a#b)'
    """
    base_url = base_url.rstrip("/")
    pattern = r"\(/.*?([^/]*?)\.md(#(?:.*?))?\)"
    replacement = rf"({base_url}/\1\2)"
    return re.sub(pattern, replacement, content)


def extract_and_mark_html_tables(content: str) -> (str, str):
    """Extract HTML tables from content and replace them with numbered markers.

    1. Find all HTML tables in the input content
    2. Replace each table with a unique marker
    3. Return both the modified content and a string containing all extracted tables

    Examples:
        >>> test_content = "Table1\\n<table><thead>Test1</thead></table>\\n\\nTable2\\n<table><thead>Test2</thead></table>\\n\\n"
        >>> modified, html_tables = extract_and_mark_html_tables(test_content)
        >>> print(html_tables) # doctest: +NORMALIZE_WHITESPACE
        TIDOCS_REPLACE_TABLE_0
        <BLANKLINE>
        <table><thead>Test1</thead></table>
        <BLANKLINE>
        TIDOCS_REPLACE_TABLE_1
        <BLANKLINE>
        <table><thead>Test2</thead></table>
        <BLANKLINE>
        <BLANKLINE>
        >>> print(modified) # doctest: +NORMALIZE_WHITESPACE
        Table1
        TIDOCS_REPLACE_TABLE_0
        <BLANKLINE>
        Table2
        TIDOCS_REPLACE_TABLE_1
    """
    TABLE_MARKER_TEMPLATE = "TIDOCS_REPLACE_TABLE_{}"
    table_pattern = re.compile(r"<table>.*?</table>", re.DOTALL)

    # Find all tables in the content
    tables = table_pattern.findall(content)

    # Initialize result containers
    extracted_tables = []
    modified_content = content

    # Process each table
    for i, table in enumerate(tables):
        marker = TABLE_MARKER_TEMPLATE.format(i)
        extracted_tables.append(f"{marker}\n\n{table}\n\n")
        modified_content = modified_content.replace(table + "\n\n", f"{marker}\n\n")

    return modified_content, "".join(extracted_tables)
