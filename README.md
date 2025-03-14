# TiDocs: Tools for TiDB Documentation

TiDocs is a toolkit that streamlines TiDB documentation workflows. It specializes in document conversion and formatting, making it easy to create professional, well-structured documentation.

## Installation

To prevent conflicts with your existing Python environment, install `tidocs` using [pipx](https://github.com/pypa/pipx#install-pipx):

```bash
pipx install tidocs
```

## Convert Markdown files to DOCX documents (New in v1.1.0)

The `tidocs.markdown_to_docx.markdown_to_docx(markdown_data, config)` function converts Markdown content into a Microsoft Word document (DOCX format). It preserves complex formatting and allows customization through a configuration object.

### Parameters

* `markdown_data`: binary content of your Markdown file.

    Read a Markdown file using `rb` mode:

    ```python
    with open("input.md", "rb") as f:
        markdown_content = f.read()
    ```

* `config`: conversion settings object containing three configuration sections:

    - `metadata`: controls document metadata and presentation. For more information, see [`metadata`](#metadata).
    - `plugin`: controls document processing behavior. For more information, see [`plugin`](#plugin).
    - `pandoc`: controls the underlying Pandoc converter. For more information, see [`pandoc`](#pandoc).

    Create from a Python dictionary or JSON file:

    ```python
    # From Python object
    from tidocs.markdown_to_docx import MarkdownToWordConfig

    config = MarkdownToWordConfig(
        metadata={...},
        plugin={...},
        pandoc={...}
    )

    # From JSON file
    import json

    with open("config.json", "r") as f:
        config_data = json.load(f)
    config = MarkdownToWordConfig(**config_data)
    ```

### Usage example

The following example shows how to convert a Markdown file to a Word document. You can find the complete source code in the [`examples/markdown_to_docx`](https://github.com/Oreoxmt/tidocs/tree/main/examples/markdown_to_docx) directory.

Python code example ([`demo.py`](https://github.com/Oreoxmt/tidocs/tree/main/examples/markdown_to_docx/demo.py)):

```python
import json
from pathlib import Path

from tidocs.markdown_to_docx import MarkdownToWordConfig, markdown_to_docx

if __name__ == "__main__":
    # Define paths for config, input, and output files
    src_path = Path(__file__).resolve().parent
    config_json = src_path / "config.json"
    input_md = src_path / "input.md"
    output_docx = src_path / "output.docx"

    print(f"Loading configuration from: {config_json}")
    # Load configuration
    with config_json.open("r") as f:
        config = json.load(f)

    # Convert Markdown to Word using the configuration
    markdown_content = input_md.read_bytes()
    word_content = markdown_to_docx(markdown_content, MarkdownToWordConfig(**config))
    output_docx.write_bytes(word_content)
    print(f"Conversion complete. Output saved to: {output_docx}")
```

Sample configuration file ([`config.json`](https://github.com/Oreoxmt/tidocs/tree/main/examples/markdown_to_docx/config.json)):

```json
{
  "metadata": {
    "title": "Document Title",
    "author": ["Author 1", "Author 2"],
    "abstract": "This is abstract.",
    "abstract_title": "Abstract",
    "date": "20250101",
    "toc_title": "Table of Contents"
  },
  "plugin": {
    "replace_internal_links": "https://oreo.life/",
    "extract_html_table": true
  },
  "pandoc": {
    "reference_doc": "/Users/test/tidocs/examples/markdown_to_docx/custom-reference.docx",
    "resource_path": ".:/Users/test/tidocs/examples/markdown_to_docx/",
    "toc": true,
    "toc_depth": 3
  }
}
```

Comparison of Markdown inputs and Word outputs:

| Input (Markdown) | Configuration | Output (Word) |
|------------------|---------------|---------------|
| - | `metadata` | ![Output (metadata)](https://github.com/Oreoxmt/tidocs/tree/main/images/example/markdown_to_docx_output_metadata.png) |
| ![Input (TOC)](https://github.com/Oreoxmt/tidocs/tree/main/images/example/markdown_to_docx_input_toc.png) | `pandoc.toc = true` and `pandoc.toc_depth = 3` | ![Output (TOC)](https://github.com/Oreoxmt/tidocs/tree/main/images/example/markdown_to_docx_output_toc.png) |
| ![Input (HTML Table)](https://github.com/Oreoxmt/tidocs/tree/main/images/example/markdown_to_docx_input_table.png) | `plugin.extract_html_table = true` | ![Output (HTML Table)](https://github.com/Oreoxmt/tidocs/tree/main/images/example/markdown_to_docx_output_table.png) |
| `[link text](/intro.md)` | `plugin.replace_internal_links = "https://oreo.life/"` | `<a href="https://oreo.life/intro">link text</a>` |
| `![image text](test.png)` | `pandoc.resource_path` | ![Output (image)](https://github.com/Oreoxmt/tidocs/tree/main/images/example/markdown_to_docx_output_image.png) |

### Configuration options

You can customize the conversion process using the following configuration sections.

#### `metadata`

Controls document metadata and presentation:

| Option           | Type        | Default | Description                        |
|-----------------|------------|---------|------------------------------------|
| `title`         | string      | `None`  | Sets the document title.                     |
| `author`        | string or list | `None`  | Specifies one or more document authors. For example: `"Author"` or `["Author 1", "Author 2"]`.                 |
| `abstract`      | string      | `None`  | Sets the document abstract.                  |
| `abstract_title` | string     | `None`  | Sets the heading for abstract section.     |
| `date`          | string      | `None`  | Sets the document date.                      |
| `toc_title`     | string      | `None`  | Sets the heading for table of contents.    |

#### `plugin`

Controls document processing behavior:

| Option                   | Type           | Default | Description                                                             |
|--------------------------|---------------|---------|-------------------------------------------------------------------------|
| `replace_internal_links` | boolean or string | `False` | Converts internal links to external format when set to a URL base. For example: `false` or `https://www.example.com`      |
| `extract_html_table`     | boolean        | `False` | Controls whether to enable special handling for HTML tables.                                |

#### `pandoc`

Controls the underlying Pandoc converter:

| Option          | Type    | Default     | Description                                                                 |
|----------------|---------|-------------|-----------------------------------------------------------------------------|
| `reference_doc` | string  | `"bundled"` | Specifies the template for the generated Word document.                                   |
| `resource_path` | string  | `None`      | Sets search paths for images and other resources. For more details, see [Pandoc documentation: `--resource-path`](https://pandoc.org/MANUAL.html#option--resource-path). |
| `toc`          | boolean | `None`      | Controls whether to enable automatic table of contents generation.                             |
| `toc_depth`    | integer | `None`      | Specifies the number of heading levels in the table of contents.            |

## Merge Release Notes (`tidocs merge`)

TiDocs addresses a common challenge in documentation workflows: converting Markdown files containing complex HTML tables into well-formatted Word or PDF documents. While traditional tools like [Pandoc](https://pandoc.org) exist, they often struggle with complex HTML tables, resulting in poorly formatted output.

For example, consider the following complex HTML table in a Markdown file:

<details>
<summary>Click to expand</summary>

```markdown
The following is an HTML table:

<table>
<thead>
  <tr>
    <th>Header 1</th>
    <th>Header 2</th>
    <th>Header 3</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td rowspan="2">Group 1</td>
    <td>Lorem ipsum odor amet, consectetuer adipiscing elit.</td>
    <td>Justo hendrerit facilities tristique ligula nostra quisque nunc potenti. Ornare porttitor elementum primis imperdiet mus.</td>
  </tr>
  <tr>
    <td>Nisi litora ornare rhoncus nunc primis molestie nullam.</td>
    <td>Urna adipiscing sollicitudin nostra facilities platea per. Ullamcorper name ut magna at sagittis nulla natoque. Lacus curabitur sagittis dictum pretium dignissim sit dolor.</td>
  </tr>
  <tr>
    <td rowspan="1">Group 2</td>
    <td>Nunc mollis tempor maecenas, morbi enim augue justo. Ut metus libero pulvinar aenean nunc.</td>
    <td>Various tortor vulputate viverra ullamcorper volutpat maximus habitasse maecenas nec. Tempor tempor facilities sem ad ultricies tincidunt imperdiet auctor. Curabitur aenean nisl scelerisque laoreet metus. Ipsum vel primis vel inceptos nulla class.</td>
  </tr>
</tbody>
</table>

The preceding is an HTML table.
```

</details>

When you convert this Markdown file to a Word or PDF document using Pandoc, you might encounter formatting issues like this:

| Pandoc Output | TiDocs Output |
| --- | --- |
| ![Pandoc Output](https://raw.githubusercontent.com/Oreoxmt/tidocs/refs/heads/main/images/example/pandoc_example_output.png) | ![TiDocs Output](https://raw.githubusercontent.com/Oreoxmt/tidocs/refs/heads/main/images/example/tidocs_example_output.png) |

Pandoc fails to maintain the table structure and formatting, resulting in a poorly formatted document. In contrast, TiDocs preserves the complex table structure and formatting, ensuring that your document looks good.

### Features

- Merge multiple Markdown files into a single document
- Preserve the formatting of complex HTML tables
- Automatically generate a table of contents
- Convert internal links like `[Overview](/overview.md)` to external links like `[Overview](https://docs.pingcap.com/tidb/stable/overview)`

### Usage

Use the `tidocs merge` command to access a web interface for combining multiple release notes into a single, well-formatted Word document.

1. Launch the application:

    ```bash
    tidocs merge
    ```

    The application will start and display a URL:

    ```bash
    ✨ Running marimo app Merge Release Notes
    🔗 URL: http://127.0.0.1:8080
    ```

    To specify a custom host and port, use:

    ```bash
    tidocs merge --host 127.0.0.1 --port 9000
    ```

    The output is as follows:

    ```bash
    ✨ Running marimo app Merge Release Notes
    🔗 URL: http://127.0.0.1:9000
    ```

2. Upload release notes:

    To merge release notes from v1.0.0 to v10.0.0, upload all files from `release-1.0.0.md` to `release-10.0.0.md`.

    ![TiDocs: Upload release notes](https://raw.githubusercontent.com/Oreoxmt/tidocs/refs/heads/main/images/usage/tidocs_merge_upload.png)

3. Configure document information:

    Fill in the fields to customize the cover page of the generated Word document.

    ![TiDocs: Configure document information](https://raw.githubusercontent.com/Oreoxmt/tidocs/refs/heads/main/images/usage/tidocs_merge_config.png)

4. Generate document:

    Click **Download Word Document** to export your formatted Word document. The document will include:

    - Properly formatted tables
    - Complete documentation links
    - Generated Table of Contents

    ![TiDocs: Generate document](https://raw.githubusercontent.com/Oreoxmt/tidocs/refs/heads/main/images/usage/tidocs_merge_download.png)

5. Post-process document:

    After generating the Word document, you can finalize it by following these steps:

    1. Open the downloaded document in Microsoft Word.

        If prompted with "This document contains fields that may refer to other files. Do you want to update the fields in this document?", click **No**.

    2. Update the table of contents:

        On the **References** tab, click **Update Table** > **Update entire table** > **OK**

    3. Optional formatting adjustments:

        - Adjust table column widths if needed.
        - If link text turns black after applying styles, use the following macro to batch update the link colors:

            ```vbscript
            Sub FormatLinks()
            Dim H As Hyperlink
            Dim themeColorRGB As Long

            themeColorRGB = ActiveDocument.Styles("Hyperlink").Font.Color

                For Each H In ActiveDocument.Hyperlinks
                    H.Range.Font.Color = themeColorRGB
                Next H

            End Sub
            ```

        - Review and adjust page breaks and heading styles.

    4. [Export Word document as PDF](https://support.microsoft.com/en-us/office/export-word-document-as-pdf-4e89b30d-9d7d-4866-af77-3af5536b974c).

## Changelog

### [1.1.0] - 2025-03-14

- Support converting Markdown files to Word documents using `tidocs.markdown_to_docx()`.
- Skip filename validation for single-file uploads in `tidocs merge`.

### [1.0.7] - 2024-12-23

- Fix the issue that HTML tables are incorrectly extracted when `<table>` tags appear in code blocks or plain text that is not part of actual HTML markup.

### [1.0.6] - 2024-12-21

- Fix the issue that hyperlinks become broken after merging Word documents due to incorrect relationship reference handling. ([#2](https://github.com/Oreoxmt/tidocs/issues/2))

### [1.0.5] - 2024-12-03

- Fix compatibility issues with Python 3.9.
- Fix formatting error when only one input file is provided.

### [1.0.4] - 2024-11-22

- Enhance the rendering of abstracts containing multiple paragraphs.

### [1.0.3] - 2024-11-22

- Remove the "Abstract" heading from the generated Word document.

### [1.0.2] - 2024-11-22

- Fix the issue that Pandoc fails to write docx output to the terminal on Windows.

### [1.0.1] - 2024-11-22

- Fix the issue that Pandoc becomes non-executable after installation on macOS because `Zipfile.extract()` doesn't maintain file permissions.

### [1.0.0] - 2024-11-21

- Support merging multiple TiDB release notes Markdown files with HTML tables into one well-formatted Word document.
