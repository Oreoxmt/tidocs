# TiDocs: Tools for TiDB Documentation

TiDocs is a toolkit that streamlines TiDB documentation workflows. It specializes in document conversion and formatting, making it easy to create professional, well-structured documentation.

## Installation

To avoid conflicts with your existing Python environment, install `tidocs` using [pipx](https://github.com/pypa/pipx#install-pipx):

```bash
pipx install tidocs
```

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
| ![Pandoc Output](/images/example/pandoc_example_output.png) | ![TiDocs Output](/images/example/tidocs_example_output.png) |

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

    ![TiDocs: Upload release notes](/images/usage/tidocs_merge_upload.png)

3. Configure document information:

    Fill in the fields to customize the cover page of the generated Word document.

    ![TiDocs: Configure document information](/images/usage/tidocs_merge_config.png)

4. Generate document:

    Click **Download Word Document** to export your formatted Word document. The document will include:

    - Properly formatted tables
    - Complete documentation links
    - Generated Table of Contents

    ![TiDocs: Generate document](/images/usage/tidocs_merge_download.png)

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
