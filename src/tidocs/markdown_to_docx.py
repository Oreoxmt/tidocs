from enum import Enum
from typing import Literal, Optional, Union
import yaml

from pydantic import AliasGenerator, BaseModel, ConfigDict
from tidocs.docx_handler import merge_documents
from tidocs.markdown_handler import (
    extract_and_mark_html_tables,
    process_internal_links,
)
from tidocs.pandoc_wrapper import Pandoc
from tidocs.util import get_reference_doc


class DocxConverter(Enum):
    """Define supported document conversion formats."""

    FROM_MARKDOWN = ("markdown", "docx")
    FROM_HTML = ("html", "docx")

    def __init__(self, source_format: str, target_format: str):
        self.source_format = source_format
        self.target_format = target_format


def snake_to_dash(text: str) -> str:
    """Convert a snake_case string to dash-case format.

    Args:
        text: String in snake_case format

    Returns:
        String converted to dash-case format

    Example:
        >>> snake_to_dash("hello_world_1")
        'hello-world-1'
    """
    return text.replace("_", "-")


class WordMetadataConfig(BaseModel):
    """Configuration for Word document metadata fields."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=snake_to_dash)
    )

    title: Optional[str] = None
    author: Union[str, list[str], None] = None
    abstract: Optional[str] = None
    abstract_title: Optional[str] = None
    date: Optional[str] = None
    toc_title: Optional[str] = None


class PluginConfig(BaseModel):
    """Configuration for Markdown processing plugins."""

    replace_internal_links: Union[Literal[False], str] = False
    extract_html_table: bool = False


class PandocConfig(BaseModel):
    """Configuration for Pandoc converter settings."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=snake_to_dash)
    )

    reference_doc: Union[Literal["bundled"], str, None] = "bundled"
    resource_path: Optional[str] = None
    toc: Optional[bool] = None
    toc_depth: Optional[int] = None


class MarkdownToWordConfig(BaseModel):
    """Main configuration for Markdown to Word conversion process."""

    metadata: WordMetadataConfig = WordMetadataConfig()
    plugin: PluginConfig = PluginConfig()
    pandoc: PandocConfig = PandocConfig()


def get_pandoc_base_options(converter: DocxConverter) -> list[str]:
    """Generate basic Pandoc conversion options.

    Args:
        converter: DocxConverter enum specifying conversion type

    Returns:
        List of base Pandoc command-line options
    """
    return [
        "-o-",  # Output to stdout
        f"--from={converter.source_format}",
        f"--to={converter.target_format}",
    ]


def generate_pandoc_options(
    pandoc_config: PandocConfig,
    converter_type: Union[Literal["md_doc"], Literal["html_doc"]],
) -> list[str]:
    """Generate complete Pandoc command-line options based on configuration.

    Args:
        pandoc_config: Configuration object containing Pandoc settings
        converter_type: Type of conversion to perform ("md_doc" or "html_doc")

    Returns:
        List of Pandoc command-line options with all configured settings
    """
    converter_map = {
        "md_doc": DocxConverter.FROM_MARKDOWN,
        "html_doc": DocxConverter.FROM_HTML,
    }
    converter = converter_map.get(converter_type)
    options = get_pandoc_base_options(converter)

    reference_doc = pandoc_config.reference_doc
    if reference_doc == "bundled":
        reference_doc = get_reference_doc()
    if reference_doc is not None:
        options.append(f"--reference-doc={reference_doc}")

    resource_path = pandoc_config.resource_path
    if resource_path is not None:
        options.append(f"--resource-path={resource_path}")

    toc = pandoc_config.toc
    if toc is not None:
        options.append(f"--toc={toc}")

    toc_depth = pandoc_config.toc_depth
    if toc_depth is not None:
        options.append(f"--toc-depth={toc_depth}")

    return options


def markdown_to_docx(markdown_data: bytes, config: MarkdownToWordConfig) -> bytes:
    """Convert Markdown content to a Word document in DOCX format.

    Args:
        markdown_data (bytes): Raw Markdown content as bytes.
        config (MarkdownToWordConfig): Configuration for the conversion process.

    Returns:
        bytes: The generated Word document as bytes.
    """
    # Generates YAML metadata block from configuration
    metadata = config.metadata
    yaml_metadata_block = (
        "\n---\n"
        + yaml.dump(
            metadata.model_dump(by_alias=True),
            sort_keys=False,
            allow_unicode=True,
            width=float("inf"),
        ).removesuffix("\n")
        + "\n---\n"
    )
    # Process Markdown content according to plugin settings:
    #  - Remove front matter if configured
    #  - Process internal links
    #  - Extract HTML tables if enabled
    md_contents = markdown_data.decode("utf-8")
    table_contents = ""
    if config.plugin.replace_internal_links is not False:
        md_contents = process_internal_links(
            md_contents, config.plugin.replace_internal_links
        )
    if config.plugin.extract_html_table:
        md_contents, table_contents = extract_and_mark_html_tables(md_contents)

    md_contents += yaml_metadata_block
    # Configure and run pandoc
    pandoc = Pandoc()
    pandoc_md_doc_options = generate_pandoc_options(config.pandoc, "md_doc")
    pandoc_html_doc_options = generate_pandoc_options(config.pandoc, "html_doc")

    md_doc_data, md_doc_err = pandoc.run(
        pandoc_md_doc_options, md_contents.encode("utf-8")
    )
    if config.plugin.extract_html_table:
        table_doc_data, table_doc_err = pandoc.run(
            pandoc_html_doc_options, table_contents.encode("utf-8")
        )
        # Merge Markdown and table documents into one
        merged_doc_data = merge_documents(md_doc_data, table_doc_data)
    else:
        merged_doc_data = md_doc_data
    return merged_doc_data
