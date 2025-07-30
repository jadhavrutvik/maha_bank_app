import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os 


APP_DIR = os.path.dirname(os.path.abspath(__file__))



BASE_URL = "https://bankofmaharashtra.in"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_soup(url):
    """
    Fetches HTML content and returns a BeautifulSoup object.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def extract_clean_main_content(url):
    """
    Extracts and cleans the main content from a specific loan page.
    Returns text inside the <ul class="normlist wrap mt-3"> tag.
    """
    try:
        soup = get_soup(url)
        if not soup:
            return {"url": url, "error": "Failed to fetch page"}

        ul_tag = soup.find("ul", class_="normlist wrap mt-3")
        if not ul_tag:
            return {"url": url, "error": "Main content not found"}

        cleaned_text = ""
        items = [item.strip() for item in ul_tag.decode_contents().split("<li>") if item.strip()]
        for item in items:
            cleaned_text += BeautifulSoup(item, "html.parser").get_text().strip()
        return {"url": url, "text": cleaned_text}
    except Exception as e:
        return {"url": url, "error": str(e)}

def extract_inner_links(main_url):
    """
    Extracts inner links and their titles from a loan page.
    Typically links under <div class="in-loan-box2">.
    """
    try:
        soup = get_soup(main_url)
        if not soup:
            return []

        inner_links = []
        cards = soup.find_all("div", class_="in-loan-box2")

        for card in cards:
            title = card.get_text(strip=True)
            a_tag = card.find_next("a", href=True)
            if a_tag:
                full_url = urljoin(BASE_URL, a_tag["href"])
                inner_links.append({"title": title, "url": full_url})
        return inner_links
    except Exception as e:
        print(f"Error extracting inner links from {main_url}: {e}")
        return []

def extract_inner_post_text(url):
    """
    Extracts full inner post content from a sub-page.
    Targets <div class="inner_post_content">.
    """
    try:
        soup = get_soup(url)
        if not soup:
            return {"url": url, "error": "Failed to fetch content"}

        content_div = soup.find("div", class_="inner_post_content")
        if not content_div:
            return {"url": url, "error": "Content not found"}

        clean_text = content_div.get_text(separator="\n", strip=True)
        return {"url": url, "text": clean_text}
    except Exception as e:
        return {"url": url, "error": str(e)}

def extract_interest_rates():
    """
    Extracts interest rate content from the interest rate page.
    """
    try:
        url = urljoin(BASE_URL, "/retail-interest-rates")
        soup = get_soup(url)
        if not soup:
            return {"url": url, "error": "Failed to fetch interest rate page"}

        body_content = soup.find("div", class_="inner_post_content")
        if not body_content:
            return {"url": url, "error": "Interest rates content not found"}

        text = body_content.get_text(separator="\n", strip=True)
        return {"url": url, "text": text}
    except Exception as e:
        return {"url": url, "error": str(e)}

def run_full_scrape():
    """
    Orchestrates the scraping process:
    - Extracts main content from personal and home loan pages.
    - Extracts sub-pages for both.
    - Adds Maha Super Flexi Housing Loan content.
    - Adds Retail Interest Rate page content.
    Returns list of all extracted data.
    """
    results = []

    try:
        # Extract main pages
        personal_url = urljoin(BASE_URL, "/personal-banking/loans/personal-loan")
        results.append({
            "type": "Personal Loan",
            "title": "Main Page",
            "data": extract_clean_main_content(personal_url).get("text", "")
        })

        home_url = urljoin(BASE_URL, "/personal-banking/loans/home-loan")
        results.append({
            "type": "Home Loan",
            "title": "Main Page",
            "data": extract_clean_main_content(home_url).get("text", "")
        })

        # Extract personal loan sub-pages
        for link in extract_inner_links(personal_url):
            result = extract_inner_post_text(link["url"])
            results.append({
                "type": "Personal Loan",
                "title": link["title"],
                "data": result.get("text", "")
            })

        # Extract home loan sub-pages
        for link in extract_inner_links(home_url):
            result = extract_inner_post_text(link["url"])
            results.append({
                "type": "Home Loan",
                "title": link["title"],
                "data": result.get("text", "")
            })

        # Maha Super Flexi Loan
        flexi_url = urljoin(BASE_URL, "/maha-super-flexi-housing-loan-scheme")
        flexi_data = extract_inner_post_text(flexi_url)
        results.append({
            "type": "Flexi Housing Loan",
            "title": "Maha Super Flexi Housing Loan Scheme",
            "data": flexi_data.get("text", "")
        })

        # Interest Rates
        interest_data = extract_interest_rates()
        results.append({
            "type": "Interest data",
            "title": "All interest data",
            "data": interest_data.get("text", "")
        })

    except Exception as e:
        results.append({"error": f"Unexpected error during scraping: {str(e)}"})

    return results


def save_to_text_files(results, ):
    """
    Saves scraped results as individual .txt files for embedding use.
    """
    output_dir = os.path.join(APP_DIR, 'scrapped_txt')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    for i, item in enumerate(results):
        type_ = item.get("type", "Unknown").replace(" ", "_")
        title = item.get("title", f"Entry_{i}").replace(" ", "_").replace("/", "_")
        filename = f"{type_}__{title}.txt"
        path = os.path.join(output_dir, filename)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(item.get("data", ""))
        except Exception as e:
            print(f"Failed to write {filename}: {e}")

    

