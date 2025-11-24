import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class CitationVerifierTool(BaseTool):
    name: str = "CitationVerifier"
    description: str = (
        "Verifies if a specific keyword or concept actually appears on a webpage. "
        "Useful for fact-checking to prevent hallucinations. "
        "Input should be a dictionary with 'url' and 'keyword'. "
        "Returns: VERIFIED if found, UNVERIFIED if not found, or Error message."
    )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError)),
        reraise=True
    )
    def _fetch_with_retry(self, url: str, headers: dict) -> requests.Response:
        """Fetch URL with automatic retry on network errors"""
        return requests.get(url, headers=headers, timeout=10)

    def _run(self, url: str, keyword: str) -> str:
        """
        Verifies if a keyword exists on a webpage.
        
        Args:
            url (str): The webpage URL to check
            keyword (str): The keyword to search for
            
        Returns:
            str: Verification result message
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            # Input validation
            if not url or not url.startswith(('http://', 'https://')):
                return f"Error: Invalid URL format. URL must start with http:// or https://"
            
            if not keyword or len(keyword.strip()) == 0:
                return f"Error: Keyword cannot be empty."
            
            # 1. Fetch Data with Retry Logic
            response = self._fetch_with_retry(url, headers)
            
            # 2. Handle HTTP Errors
            if response.status_code != 200:
                return f"Error: URL returned status code {response.status_code}. Cannot verify."

            # 3. Parse Content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements for cleaner text
            for script in soup(["script", "style"]):
                script.decompose()
                
            text_content = soup.get_text(separator=' ', strip=True).lower()
            
            # 4. Verification Logic (case-insensitive)
            keyword_lower = keyword.lower()
            if keyword_lower in text_content:
                # Count occurrences for confidence metric
                occurrence_count = text_content.count(keyword_lower)
                return (f"✅ VERIFIED: The keyword '{keyword}' was found {occurrence_count} time(s) in {url}. "
                       f"This source can be cited with confidence.")
            else:
                return (f"❌ UNVERIFIED: The keyword '{keyword}' was NOT found in the page text. "
                       f"Do not use this source for claims about '{keyword}'.")

        except requests.exceptions.Timeout:
            return f"⚠️ System Error: Request timed out after 10 seconds. URL may be slow or unreachable: {url}"
        
        except requests.exceptions.RequestException as e:
            return f"⚠️ System Error: Network error occurred. Details: {str(e)}"
        
        except Exception as e:
            return f"⚠️ System Error: Failed to verify citation. Details: {str(e)}"