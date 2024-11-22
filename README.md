# TiDocs: Tools for TiDB Documentation

A toolkit for streamlining TiDB documentation workflows, specializing in document conversion and formatting.

## Installation

```bash
pip install tidocs
```

## Merge Release Notes (`tidocs merge`)

This addresses a common challenge in documentation workflows: converting Markdown files containing HTML tables into well-formatted Word and PDF documents. While traditional tools like [Pandoc](https://pandoc.org) exist, they often struggle with complex HTML tables, resulting in poorly formatted output.

### Features

- Merge multiple Markdown files into a single document
- Preserve complex HTML table formatting
- Create automated table of contents
- Convert internal links `[Overview](/overview.md)` to external links `[Overview](https://docs.pingcap.com/tidb/stable/overview)`.

### Usage

The `tidocs merge` command provides a web interface for combining multiple release notes into a single, well-formatted Word document.

1. Launch the application

    ```bash
    pip install tidocs
    tidocs merge
    ```
  
    The application will start and display a URL:
  
    ```bash
    ✨ Running marimo app Merge Release Notes
    🔗 URL: http://127.0.0.1:8080
    ```

2. Upload release notes

    To merge release notes from v1.0.0 to v10.0.0, upload all files from `release-1.0.0.md` to `release-10.0.0.md`.

3. Configure document information

    These fields will appear on the cover page of the generated Word document.

4. Generate document

    Click **Download Word Document** to export your formatted Word document. The document will include:

    - Properly formatted tables
    - Complete documentation links
    - Generated Table of Contents

5. Post-process document

    After generating the Word document, follow these steps to finalize it:

    1. Open the downloaded document in Microsoft Word.
    2. Update the table of contents:

      On the **References** tab, click **Update Table** > **Update entire table** > **OK**

    3. Optional formatting adjustments:

      - Adjust table column widths if needed.
      - Review and adjust page breaks.
      - Check and adjust heading styles.

    4. [Export Word document as PDF](https://support.microsoft.com/en-us/office/export-word-document-as-pdf-4e89b30d-9d7d-4866-af77-3af5536b974c).

## Changelog

### v1.0.4

- Enhance the rendering of abstracts containing multiple paragraphs.

### v1.0.3

- Remove "Abstract" heading from the generated Word document.

### v1.0.2

- Fix the issue that Pandoc fails to write docx output to terminal on Windows.

### v1.0.1

- Fix the issue that Pandoc becomes non-executable after installation on macOS because `Zipfile.extract()` doesn't maintain file permissions.

### v1.0.0

- Support merging multiple TiDB release notes Markdown files with HTML tables into one well-formatted Word document.
