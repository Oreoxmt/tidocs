import marimo

__generated_with = "0.9.20"
app = marimo.App(app_title="TiDocs - Merge Release Notes")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        """
        # TiDocs: Merge Release Notes

        #### Merge and convert TiDB release notes from Markdown to a well-formatted Word document in seconds.
        """
    )
    return


@app.cell
def __(upload_area):
    upload_area
    return


@app.cell
def __(is_valid_filename, md_files, mo):
    for i in range(len(md_files.value)):
        mo.stop(
            not is_valid_filename(md_files.value[i].name),
            mo.md(
                f'#### {mo.icon("ic:round-error-outline", color="darkorange", inline=True)} Invalid format.\n\nPlease upload release notes in `release-x.y.z.md` format.'
            )
            .center()
            .callout(kind="danger"),
        )
    return (i,)


@app.cell
def __(config_area):
    config_area
    return


@app.cell
def __(merged_doc, mo):
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
def __(
    abstract_input,
    authors_input,
    date_input,
    generate_pandoc_metadata,
    title_input,
    toc_title_input,
):
    metadata = generate_pandoc_metadata(
        title=title_input.value,
        author=authors_input.value,
        publication_date=date_input.value,
        abstract=abstract_input.value,
        toc_title=toc_title_input.value,
    )
    return (metadata,)


@app.cell
def __(mo):
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
def __(mo):
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
def __(
    base_url_input,
    extract_and_mark_html_tables,
    md_files,
    metadata,
    process_internal_links,
    remove_front_matter,
):
    import re


    def is_valid_filename(filename: str) -> bool:
        """Validate uploaded files match release note pattern."""
        pattern = r"release-\d+\.\d+\.\d+\.md"
        return re.match(pattern, filename) is not None


    def extract_version(filename):
        """Extract the version number from the filename"""
        return tuple(map(int, filename.name.split("-")[1].split(".")[:-1]))


    # Sort files by version number in descending order.
    sorted_md_files = sorted(md_files.value, key=extract_version, reverse=True)

    md_contents = metadata
    for md_file in sorted_md_files:
        md_contents += remove_front_matter(md_file.contents).decode("utf-8") + "\n"

    md_contents = process_internal_links(md_contents, base_url_input.value)
    md_contents, table_contents = extract_and_mark_html_tables(md_contents)
    return (
        extract_version,
        is_valid_filename,
        md_contents,
        md_file,
        re,
        sorted_md_files,
        table_contents,
    )


@app.cell
def __(Pandoc, get_reference_doc, md_contents, mo, table_contents):
    reference_doc = get_reference_doc()

    pandoc = Pandoc()

    md_doc_data, md_doc_err = pandoc.run(
        [
            "-o-",
            f"--reference-doc={reference_doc}",
            "--to=docx",
            "--from=markdown",
            "--toc=true",
            "--toc-depth=3",
            "--metadata=abstract-title:",
        ],
        md_contents.encode("utf-8"),
    )

    mo.stop(
        md_doc_err.decode("utf-8") != "",
        mo.md(
            f'#### {mo.icon("ic:round-error-outline", color="darkorange", inline=True)} Failed to convert to Word.\n\n{md_doc_err.decode("utf-8")}'
        )
        .center()
        .callout(kind="danger"),
    )

    table_doc_data, table_doc_err = Pandoc().run(
        [
            "-o-",
            f"--reference-doc={reference_doc}",
            "--to=docx",
            "--from=html",
        ],
        table_contents.encode("utf-8"),
    )

    mo.stop(
        table_doc_err.decode("utf-8") != "",
        mo.md(
            f'####{mo.icon("ic:round-error-outline", color="darkorange", inline=True)} Failed to convert to Word.\n\n{table_doc_err.decode("utf-8")}'
        )
        .center()
        .callout(kind="danger"),
    )
    return (
        md_doc_data,
        md_doc_err,
        pandoc,
        reference_doc,
        table_doc_data,
        table_doc_err,
    )


@app.cell
def __(md_doc_data, merge_documents, mo, table_doc_data):
    merged_doc_data = merge_documents(md_doc_data, table_doc_data)

    merged_doc = mo.download(
        data=merged_doc_data,
        filename="tidocs_generated_doc.docx",
        label="Download Word Document",
    )
    return merged_doc, merged_doc_data


@app.cell
def __(mo):
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


@app.cell
def __():
    from tidocs.markdown_handler import (
        generate_pandoc_metadata,
        remove_front_matter,
        process_internal_links,
        extract_and_mark_html_tables,
    )
    from tidocs.docx_handler import merge_documents
    from tidocs.pandoc_wrapper import Pandoc
    from tidocs.util import get_reference_doc
    return (
        Pandoc,
        extract_and_mark_html_tables,
        generate_pandoc_metadata,
        get_reference_doc,
        merge_documents,
        process_internal_links,
        remove_front_matter,
    )


if __name__ == "__main__":
    app.run()
