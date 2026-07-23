from io import BytesIO

from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, StreamObject


def make_text_pdf(text: str) -> bytes:
    """Build a minimal text-based PDF for tests (no external fixtures)."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    escaped = (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET"
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {
                    NameObject("/F1"): DictionaryObject(
                        {
                            NameObject("/Type"): NameObject("/Font"),
                            NameObject("/Subtype"): NameObject("/Type1"),
                            NameObject("/BaseFont"): NameObject("/Helvetica"),
                        }
                    )
                }
            )
        }
    )
    contents = StreamObject()
    contents.set_data(stream.encode("latin-1"))
    page[NameObject("/Contents")] = contents
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()
