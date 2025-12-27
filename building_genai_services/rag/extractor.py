from pypdf import PdfReader


def pdf_text_extractor(filepath: str) -> None:
    content = ""
    pdf_reader = PdfReader(filepath, strict=True)  #strict=True so that any read errors are logged to the terminal
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            content += f"{page_text}\n\n"
    with open(filepath.replace("pdf", "txt"), "w", encoding="utf-8") as file:
        file.write(content)
