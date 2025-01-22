import marimo

__generated_with = "0.10.15"
app = marimo.App(app_title="TiDocs - Merge Release Notes")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # TiDocs: Merge Release Notes

        #### Merge and convert TiDB release notes from Markdown to a well-formatted Word document in seconds.
        """
    )
    return


@app.cell
def _(upload_area):
    upload_area
    return


@app.cell
def _(md_files, mo, validate_process_uploaded_files):
    is_valid, result = validate_process_uploaded_files(md_files)

    mo.stop(
        not is_valid,
        mo.md(
            f"#### {mo.icon('ic:round-error-outline', color='darkorange', inline=True)} Invalid format."
            "\n\n"
            f"Please upload release notes in `release-x.y.z.md` format. "
            "Invalid files:\n\n" + "\n".join(f"- {item}" for item in result)
        )
        .center()
        .callout(kind="danger"),
    )

    md_contents = result
    return is_valid, md_contents, result


@app.cell
def _(config_area):
    config_area
    return


@app.cell
def _(merged_doc, mo):
    download_area = mo.vstack(
        [
            mo.md(f"""## {mo.icon('fluent:document-one-page-multiple-sparkle-24-regular')}  3. Generate Document
            Click the button below to download your formatted Word document. The document will include:

            - Properly formatted tables
            - Complete documentation links
            - Generated Table of Contents
    """),
            merged_doc.center(),
        ]
    )
    download_area
    return (download_area,)


@app.cell
def _(
    MarkdownToWordConfig,
    PandocConfig,
    PluginConfig,
    WordMetadataConfig,
    abstract_input,
    authors_input,
    base_url_input,
    date_input,
    markdown_to_word,
    md_contents,
    mo,
    title_input,
    toc_title_input,
):
    config = MarkdownToWordConfig(
        metadata=WordMetadataConfig(
            title=title_input.value if len(title_input.value) > 0 else None,
            author=authors_input.value.split(",")
            if len(authors_input.value) > 0
            else None,
            abstract=abstract_input.value
            if len(abstract_input.value) > 0
            else None,
            abstract_title="",
            toc_title=toc_title_input.value,
            date=date_input.value.strftime("%Y%m%d"),
        ),
        plugin=PluginConfig(
            remove_front_matter=True,
            replace_internal_links=base_url_input.value
            if len(base_url_input.value) > 0
            else False,
            extract_html_table=True,
        ),
        pandoc=PandocConfig(reference_doc="bundled", toc=True, toc_depth=3),
    )

    merged_doc_data = markdown_to_word(md_contents, config)

    merged_doc = mo.download(
        data=merged_doc_data,
        filename="tidocs_generated_doc.docx",
        label="Download Word Document",
    )
    return config, merged_doc, merged_doc_data


@app.cell
def _(mo):
    md_files = mo.ui.file(
        filetypes=[".md"],
        multiple=True,
        kind="area",
        label="Drag and drop Markdown files here, or click to browse.",
    )
    upload_area = mo.vstack(
        [
            mo.md(f"""## {mo.icon('lucide:files')} 1. Upload Release Notes

        To merge release notes from v1.0.0 to v10.0.0, upload all files from `release-1.0.0.md` to `release-10.0.0.md`.
    """),
            md_files,
        ]
    )
    return md_files, upload_area


@app.cell
def _(mo):
    config_area_title = mo.md(
        f"""## {mo.icon('lucide:edit')} 2. Configure Document Information

        These fields will appear on the cover page of the generated Word document.
        """
    )

    title_input = mo.ui.text(
        label="Title",
        placeholder="Enter the document title",
        full_width=True,
    )
    authors_input = mo.ui.text(
        label="Authors",
        placeholder="Enter authors' names, separated by commas",
        full_width=True,
    )
    abstract_input = mo.ui.text_area(
        label="Abstract",
        placeholder="Write the abstract in Markdown format",
        rows=8,
        full_width=True,
    )
    date_input = mo.ui.date(label="Publication Date", full_width=True)
    toc_title_input = mo.ui.dropdown(
        options=["目录", "Table of Contents"],
        label="Table of Contents Title",
        full_width=True,
    )
    base_url_input = mo.ui.text(
        placeholder="Provide the base URL for internal links",
        label="Documentation Base URL",
        kind="url",
        full_width=True,
    )
    config_area = mo.vstack(
        [
            config_area_title,
            title_input,
            authors_input,
            abstract_input,
            base_url_input,
            mo.hstack([date_input, toc_title_input]),
        ]
    )
    return (
        abstract_input,
        authors_input,
        base_url_input,
        config_area,
        config_area_title,
        date_input,
        title_input,
        toc_title_input,
    )


@app.cell
def _(Union):
    import re


    def is_valid_filename(filename: str) -> bool:
        """Validate if filename matches the release note pattern 'release-x.y.z.md'.

        >>> is_valid_filename('release-1.2.3.md')
        True
        >>> is_valid_filename('release-10.20.30.md')
        True
        >>> is_valid_filename('release-1.2.3.txt')
        False
        >>> is_valid_filename('release-a.b.c.md')
        False
        >>> is_valid_filename("invalid-filename.md")
        False
        >>> is_valid_filename('')
        False
        """
        pattern = r"release-\d+\.\d+\.\d+\.md"
        return re.match(pattern, filename) is not None


    def extract_version(filename):
        """Extract the version numbers from a release filename as a tuple.

        >>> class MockFile:
        ...     def __init__(self, name):
        ...         self.name = name
        >>> extract_version(MockFile("release-1.2.3.md"))
        (1, 2, 3)
        >>> extract_version("release-1.2.3.md")
        (1, 2, 3)
        >>> extract_version("release-10.20.30.md")
        (10, 20, 30)
        """
        filename_str = filename if isinstance(filename, str) else filename.name
        return tuple(map(int, filename_str.split("-")[1].split(".")[:-1]))


    def validate_process_uploaded_files(md_files) -> (bool, Union[bytes, list]):
        """Validate and process uploaded Markdown files based on their filenames and versions.

        This function handles both single and multiple Markdown file uploads. For multiple files, it validates filenames against the 'release-x.y.z.md' format and concatenates them in descending version order.

        Args:
            md_files: An object containing uploaded Markdown files. It provides access to file names and contents.

        Returns:
            tuple: A pair containing:
                - bool: True if processing succeeded, False if validation failed.
                - Union[bytes, list]: Either:
                    - bytes: Concatenated contents of all files if successful.
                    - list: List of invalid filenames if validation failed.

        Processing steps:
            1. If only one file is uploaded, return its content without validating the file name.
            2. If multiple files are uploaded:
                - Validate file names against the `release-x.y.z.md` format.
                - Return a list of invalid file names if any.
                - Otherwise, sort the files by version number in descending order and concatenate their contents into a single file.
        """
        total_md_files = len(md_files.value)

        if total_md_files == 1:
            return (True, md_files.contents())

        md_contents: bytes = b""
        invalid_filenames = []

        for i in range(total_md_files):
            if not is_valid_filename(md_files.name(i)):
                invalid_filenames.append(md_files.name(i))

        if len(invalid_filenames) > 0:
            return (False, invalid_filenames)

        # Sort files by version number in descending order.
        sorted_md_files = sorted(md_files.value, key=extract_version, reverse=True)
        for md_file in sorted_md_files:
            md_contents += md_file.contents + b"\n"

        return (True, md_contents)
    return (
        extract_version,
        is_valid_filename,
        re,
        validate_process_uploaded_files,
    )


@app.cell
def _(mo):
    mo.md(f"""## {mo.icon('icon-park-outline:format')} 4. Post-process Document

    After generating the Word document, follow these steps to finalize it:

    1. Open the downloaded document in Microsoft Word.
    2. Update the table of contents:

        On the **References** tab, click **Update Table** > **Update entire table** > **OK**

    3. Optional formatting adjustments:

        - Adjust table column widths if needed.
        - Review and adjust page breaks.
        - Check and adjust heading styles.

    4. [Export Word document as PDF](https://support.microsoft.com/en-us/office/export-word-document-as-pdf-4e89b30d-9d7d-4866-af77-3af5536b974c).
    """)
    return


@app.cell(disabled=True)
def test_func(extract_version, is_valid_filename, mo):
    is_valid_filename
    extract_version

    import doctest

    failures, success = doctest.testmod(verbose=True)
    mo.md(f"Test Result:\n\nSuccess: {success}, Failures: {failures}")
    return doctest, failures, success


@app.cell
def _():
    from typing import Union

    from tidocs.markdown_to_word import (
        WordMetadataConfig,
        PluginConfig,
        PandocConfig,
        MarkdownToWordConfig,
        markdown_to_word,
    )
    return (
        MarkdownToWordConfig,
        PandocConfig,
        PluginConfig,
        Union,
        WordMetadataConfig,
        markdown_to_word,
    )


if __name__ == "__main__":
    app.run()
