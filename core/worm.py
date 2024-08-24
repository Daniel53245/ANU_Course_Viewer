import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time
from . import course

ProgrameAndCoursePage = "https://programsandcourses.anu.edu.au"
_MIN_YEAR = 2020


class BasicCrawler:
    def __init__(self, start_url, max_depth=2):
        self.start_url = start_url
        self.max_depth = max_depth
        self.current_url = None
        self.visited = set()
        self.status = 1
        self.crawled_courses = []

    def crawl(self):
        self._crawl_page(self.start_url, 0)

    def _crawl_page(self, url, depth):
        if depth > self.max_depth or url in self.visited:
            return 0

        print(f"Crawling: {url} (Depth: {depth})")
        self.visited.add(url)
        self.current_url = url
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to retrieve {url}")
                return
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            self.status = -1
            return

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title").get_text() if soup.find("title") else "No Title"
        # if the page is not found
        if title == "Page not found":
            print("Page not found: maybe year is too new")
            url = lower_year_in_url(url)
            if url == -1:
                print(
                    "No more year to go back,the course may be no longer offered or not created yet"
                )
                return
            self._crawl_page(url, depth)
            return

        self._process_page(soup)
        for elem in self._get_requisite(soup):
            tag = elem["href"]
            url = urljoin(ProgrameAndCoursePage, tag)
            if self._is_course_page(url):
                print(f"INFO:rawling prequsite course url:{url}")
                self._crawl_page(url, depth + 1)

        time.sleep(0.5)  # Be polite to the server

    def _process_page(self, soup):
        title = soup.find("title").get_text() if soup.find("title") else "No Title"
        # if there is no elem in list with this ur
        this_course = course.Course(title)
        this_course.course_url = self.current_url
        this_course.course_code = extract_course_code(self.current_url)
        # find inhereietn requiremnts
        inherent_requirements = self._get_inherent_reqirement(soup)
        print(f"Inherent Requirements: {inherent_requirements.get_text()}")
        # find prequsite courses and add them into the searching list
        prequsites = self._get_requisite(soup)
        print("Requisite Courses:")

        for prequsite in prequsites:
            this_course.add_prequisite(extract_course_code(prequsite["href"]))
            print(f"{prequsite.get_text()} ({prequsite['href']})")

        self.crawled_courses.append(this_course)

    def _get_inherent_reqirement(self, soup):
        """
        In the page there is a h2 with id inherent-requirements"
        get the sibliting of it and the bs obejct of the element

        param: soup: bs object of the page
        return: bs object of the element
        """
        try:
            elem = soup.find("h2", id="inherent-requirements")
            if elem is None:
                print(f"No Inehereient Requiremnt for the course {self.current_url}")
            content = elem.find_next_sibling()

            if content.name != "p":
                raise ValueError(
                    "Anu wbepage formatting unexpected:Not <p> following inherent-requirements h2"
                )
        except Exception as e:
            print(
                f"Error:error occuring during getting inherent requirement in {self.current_url}, I will give you empty content"
            )
            return BeautifulSoup("<p>empty</p>", "html.parser")
        return content

    def _get_requisite(self, soup):
        """
        In the page there is a h2 with class requisite the div after it contains serval <a> tage where are links
        to the reuisite course linke

        param: soup: bs object of the page
        return: list of bs object(<a>) where link prequsite course
        """
        elem = soup.find("div", class_="requisite")
        if elem == None:
            print(f"Info:No Requisite found on page for the course:{self.current_url}")
            return []
        return elem.find_all("a")

    def _is_course_page(self, string):
        """
        Check if a url is about a course
        """
        pattern = (
            r"^https://programsandcourses\.anu\.edu\.au/\d{4}/course/[A-Z]{4}\d{4}$"
        )
        return re.match(pattern, string) is not None


def lower_year_in_url(url, min_year=_MIN_YEAR):
    """
    Automatically lowers the year in the URL.

    Parameters:
    - url (str): The original URL.
    - min_year (int): The minimum year to decrement to (default is 2000).

    Returns:
    - str: The new URL with the year decremented, or the original URL if no valid year is found.
    - -1 if it already reaches the min_year
    """
    # Parse the URL to extract components
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")

    # Identify and decrement the year part in the path
    for i, part in enumerate(path_parts):
        if part.isdigit() and len(part) == 4:  # Check if it's a year
            current_year = int(part)
            if current_year > min_year:
                current_year -= 1
                path_parts[i] = str(current_year)
                new_path = "/".join(path_parts)
                return urlunparse(parsed_url._replace(path=new_path))
            else:
                return -1
            # Break after processing the year part


def extract_course_code(url_str):
    # Extract the course code from the URL
    return url_str.split("/")[-1]


if __name__ == "__main__":
    start_url = "https://example.com"
    crawler = BasicCrawler(start_url, max_depth=2)
    crawler.crawl()
