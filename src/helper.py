from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_pdf_files(folder: str):
    loader = DirectoryLoader(
        folder, glob="*.pdf",
        loader_cls=PyPDFLoader, show_progress=True
    )
    return loader.load()

def process_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""],
        add_start_index=True
    )
    return splitter.split_documents(documents)
