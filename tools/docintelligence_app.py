from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from typing import TypedDict, List
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from typing_extensions import Annotated
from dotenv import load_dotenv
import os
load_dotenv()  # Load environment variables from .env file
# Initialize the DocumentAnalysisClient
endpoint = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
api_key = os.getenv("AZURE_API_KEY")

if not endpoint or not api_key:
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Type assertion for mypy
assert isinstance(endpoint, str)
assert isinstance(api_key, str)

class DocumentPage(TypedDict):
    content: str
    page_number: int

class DocumentAnalysisResult(TypedDict):
    pages: List[DocumentPage]
    total_pages: int

class DocIntelligenceApp:
    def __init__(self):
        self.client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

    @kernel_function
    async def analyze_document(self, pdf_file_path: Annotated[str, "Path to the PDF file to analyze"]) -> DocumentAnalysisResult:
        """Analyze a PDF document and extract text content."""
        with open(pdf_file_path, "rb") as pdf_file:
            poller = self.client.begin_analyze_document("prebuilt-layout", document=pdf_file)
            result = poller.result()
        
        # Build response structure
        pages = []
        for page_idx, page in enumerate(result.pages):
            page_text = ""
            for line in page.lines:
                page_text += line.content + " "
            pages.append({
                "content": page_text.strip(),
                "page_number": page.page_number
            })
        
        return {
            "pages": pages,
            "total_pages": len(result.pages)
        }

    @kernel_function
    async def get_document_summary(self, pdf_file_path: Annotated[str, "Path to the PDF file to summarize"]) -> str:
        """Get a concise summary of the document content."""
        from .text_chunker import chunk_text
        result = await self.analyze_document(pdf_file_path)
        total_content = " ".join([page["content"] for page in result["pages"]])
        chunks = chunk_text(total_content)
        # Return first chunk summary with total page count
        return f"Document contains {result['total_pages']} pages. Content from first section: {chunks[0][:2000]}..."


    @kernel_function
    async def extract_text_from_page(self, pdf_file_path: Annotated[str, "Path to the PDF file"], page_number: Annotated[int, "Page number to extract"]) -> str:
        """Extract text content from a specific page."""
        result = await self.analyze_document(pdf_file_path)
        
        if page_number <= 0 or page_number > result["total_pages"]:
            return f"Invalid page number. Document has {result['total_pages']} pages."
        
        page = result["pages"][page_number - 1]
        return page["content"]
