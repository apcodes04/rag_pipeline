from pathlib import Path
from typing import List, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders import JSONLoader

def load_all_documents(data_dir: str) -> List[Any]:
    """
    Load all supported files from the data directory.
    Supported: PDF, TXT, CSV, Excel, Word, JSON
    """
    data_path = Path(data_dir).resolve()
    print(f"[DEBUG] Data path: {data_path}")
    documents = []

    # PDF files
    pdf_files = list(data_path.glob('**/*.pdf'))
    print(f"[DEBUG] Found {len(pdf_files)} PDF files")
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_file))
            loaded = loader.load()
            documents.extend(loaded)
            print(f"[DEBUG] Loaded {len(loaded)} pages from {pdf_file.name}")
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {pdf_file}: {e}")

    # TXT files
    txt_files = list(data_path.glob('**/*.txt'))
    print(f"[DEBUG] Found {len(txt_files)} TXT files")
    for txt_file in txt_files:
        try:
            loader = TextLoader(str(txt_file))
            loaded = loader.load()
            documents.extend(loaded)
            print(f"[DEBUG] Loaded {len(loaded)} docs from {txt_file.name}")
        except Exception as e:
            print(f"[ERROR] Failed to load TXT {txt_file}: {e}")

    # CSV files
    csv_files = list(data_path.glob('**/*.csv'))
    print(f"[DEBUG] Found {len(csv_files)} CSV files")
    for csv_file in csv_files:
        try:
            loader = CSVLoader(str(csv_file))
            loaded = loader.load()
            documents.extend(loaded)
            print(f"[DEBUG] Loaded {len(loaded)} docs from {csv_file.name}")
        except Exception as e:
            print(f"[ERROR] Failed to load CSV {csv_file}: {e}")

    # Excel files
    xlsx_files = list(data_path.glob('**/*.xlsx'))
    print(f"[DEBUG] Found {len(xlsx_files)} Excel files")
    for xlsx_file in xlsx_files:
        try:
            loader = UnstructuredExcelLoader(str(xlsx_file))
            loaded = loader.load()
            documents.extend(loaded)
            print(f"[DEBUG] Loaded {len(loaded)} docs from {xlsx_file.name}")
        except Exception as e:
            print(f"[ERROR] Failed to load Excel {xlsx_file}: {e}")

    # Word files
    docx_files = list(data_path.glob('**/*.docx'))
    print(f"[DEBUG] Found {len(docx_files)} Word files")
    for docx_file in docx_files:
        try:
            loader = Docx2txtLoader(str(docx_file))
            loaded = loader.load()
            documents.extend(loaded)
            print(f"[DEBUG] Loaded {len(loaded)} docs from {docx_file.name}")
        except Exception as e:
            print(f"[ERROR] Failed to load Word {docx_file}: {e}")

    # JSON files
    json_files = list(data_path.glob('**/*.json'))
    print(f"[DEBUG] Found {len(json_files)} JSON files")
    for json_file in json_files:
        try:
            loader = JSONLoader(str(json_file))
            loaded = loader.load()
            documents.extend(loaded)
            print(f"[DEBUG] Loaded {len(loaded)} docs from {json_file.name}")
        except Exception as e:
            print(f"[ERROR] Failed to load JSON {json_file}: {e}")

    print(f"[DEBUG] Total loaded documents: {len(documents)}")
    return documents

if __name__ == "__main__":
    docs = load_all_documents("data")
    print(f"Loaded {len(docs)} documents.")
    print("Example document:", docs[0] if docs else None)