from app.indexing.discovery import DiscoveredFile, discovered_file_from_document
from app.ingestion.models import ExtractedDocument


def discovered_files_from_documents(
    documents: list[ExtractedDocument],
) -> list[DiscoveredFile]:
    return [discovered_file_from_document(document) for document in documents]
