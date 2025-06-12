import re
from utils.scraper import WebScraper
from utils.embedding import EmbeddingGenerator
from db.vectorstore import PGVectorStore

class DocumentService:
    CONSTANT_XPATH = "/html/body/div[3]/main/div/div[3]"

    def __init__(self):
        self.scraper = WebScraper()
        self.embedding_generator = EmbeddingGenerator()
        
    def scrape_and_store(self, url: str, collection_name: str, source_identifier: str):
        """Scrapes, cleans, chunks, embeds, and stores documentation from a URL."""
        try:
            document_text = self.scraper.scrape_by_xpath(url, self.CONSTANT_XPATH)
            cleaned_data = self._clean_text(document_text)
            chunks = self.scraper.chunk_text(cleaned_data)
            embeddings = self.embedding_generator.generate_embeddings(chunks)
            vector_store = PGVectorStore(collection_name=collection_name)
            vector_store.store_embeddings(chunks, embeddings, source_identifier)
            
            return "Document scraped, processed, and stored successfully."
        except Exception as e:
            raise Exception(f"An error occurred while processing the document: {e}")

    def _clean_text(self, text: str) -> str:
        """Helper function to clean the scraped text."""
        text = " ".join(text.replace("OptScale", "Cloudtuner").split())
        text = text.replace(". Cloudtuner", ".\nCloudtuner")
        text = re.sub(r'\n', '', text)
        return text
