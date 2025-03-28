from lxml import html
import requests
from nltk.tokenize import sent_tokenize



class WebScraper:
    def scrape_by_xpath(self, url: str, xpath: str) -> str:
        """
        Scrapes content from the given URL using the provided XPath.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            tree = html.fromstring(response.content)
            results = tree.xpath(xpath)
            if results:
                extracted_text = []
                for result in results:
                    if hasattr(result, "text_content"):
                        extracted_text.append(result.text_content().strip())
                    else:
                        extracted_text.append(str(result).strip())
                return "\n".join(extracted_text)
            else:
                return "No data found for the provided XPath."
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error scraping {url}: {e}")

    def chunk_text(self, text: str, chunk_size=400, overlap=50) -> list:
        """Chunks the scraped text into smaller parts using sentence-based chunking."""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len((current_chunk + " " + sentence).split()) <= chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

