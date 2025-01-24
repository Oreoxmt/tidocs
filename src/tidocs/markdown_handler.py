import re


def remove_front_matter(content: bytes) -> bytes:
    """Remove the first YAML front matter block from document content.

    Args:
        content (bytes): Raw document content as bytes

    Returns:
        bytes: Document content with the first front matter block removed. If no valid front matter block is found (missing delimiters or incorrect positioning), returns the original content unchanged.

    Examples:
        >>> remove_front_matter(b"Test\\n-\\ntitle\\nTest")
        b'Test\\n-\\ntitle\\nTest'
        >>> remove_front_matter(b"---\\ntitle:Test\\nsummary:Test\\n---\\nLine")
        b'Line'
        >>> remove_front_matter(b"Test\\n---\\ntitle:Test\\nsummary:Test\\n---\\nLine")
        b'Test\\nLine'
        >>> remove_front_matter(b"Test\\n---\\ntitle:Test\\nsummary:Test\\n---\\nLine\\n---\\ntitle:Test\\nsummary:Test\\n---\\nLine")
        b'Test\\nLine\\n---\\ntitle:Test\\nsummary:Test\\n---\\nLine'
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
        >>> print(html_tables)
        TIDOCS_REPLACE_TABLE_0
        <BLANKLINE>
        <table><thead>Test1</thead></table>
        <BLANKLINE>
        TIDOCS_REPLACE_TABLE_1
        <BLANKLINE>
        <table><thead>Test2</thead></table>
        <BLANKLINE>
        <BLANKLINE>
        >>> print(modified)
        Table1
        TIDOCS_REPLACE_TABLE_0
        <BLANKLINE>
        Table2
        TIDOCS_REPLACE_TABLE_1
        <BLANKLINE>
        <BLANKLINE>
        >>> test_content = "Content <table> </table>"
        >>> modified, html_tables = extract_and_mark_html_tables(test_content)
        >>> modified == test_content
        True
        >>> len(html_tables) == 0
        True
        >>> test_content = "Table1\\n    <table><thead>Test1</thead>    </table>\\n\\nTable2\\n  <table><thead>Test2</thead></table>\\n\\n"
        >>> modified, html_tables = extract_and_mark_html_tables(test_content)
        >>> print(html_tables)
        TIDOCS_REPLACE_TABLE_0
        <BLANKLINE>
        <table><thead>Test1</thead>    </table>
        <BLANKLINE>
        TIDOCS_REPLACE_TABLE_1
        <BLANKLINE>
        <table><thead>Test2</thead></table>
        <BLANKLINE>
        <BLANKLINE>
        >>> print(modified)
        Table1
            TIDOCS_REPLACE_TABLE_0
        <BLANKLINE>
        Table2
          TIDOCS_REPLACE_TABLE_1
        <BLANKLINE>
        <BLANKLINE>
    """
    TABLE_MARKER_TEMPLATE = "TIDOCS_REPLACE_TABLE_{}"
    # Capture whitespace between newline and table
    table_pattern = re.compile(r"\n(\s*?)(<table>.*?</table>)", re.DOTALL)

    # Find all tables and their positions along with whitespace
    tables = []
    for match in table_pattern.finditer(content):
        whitespace = match.group(1)
        table = match.group(2)
        tables.append((whitespace, table, match.start()))

    # Initialize result containers
    extracted_tables = []
    modified_content = content

    # Process each table in reverse order to maintain correct positions
    for i, (whitespace, table, _) in enumerate(reversed(tables)):
        marker = TABLE_MARKER_TEMPLATE.format(len(tables) - i - 1)
        extracted_tables.insert(0, f"{marker}\n\n{table}\n\n")
        # Replace the table while preserving whitespace
        modified_content = modified_content.replace(
            f"\n{whitespace}{table}", f"\n{whitespace}{marker}"
        )

    return modified_content, "".join(extracted_tables)
