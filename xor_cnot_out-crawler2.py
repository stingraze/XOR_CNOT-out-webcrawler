import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import sys

class XOR_CNOT_OUTCrawle:
    def __init__(self, start_url, max_depth=15, grid_size=5, target_words=None):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()
        self.grid_size = grid_size
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        self.current_position = [0, 0]
        self.target_words = target_words if target_words else []

    def crawl(self):
        self.display_grid()  # Display initial dark grid
        time.sleep(1)  # Pause to show initial state
        self.recursive_crawl(self.start_url, 0)

    def recursive_crawl(self, url, depth):
        if depth > self.max_depth or url in self.visited:
            return

        self.visited.add(url)
        print(f"Crawling: {url}")

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract links
            links = soup.find_all('a', href=True)
            valid_links = [urljoin(url, link['href']) for link in links if link['href'].startswith('/') or link['href'].startswith(self.start_url)]

            # Check for target words and trigger gates
            page_text = soup.get_text()
            if self.match_target_words(page_text):
                print("Target words matched! Triggering XOR and CNOT gates.")
                self.update_grid(page_text)

            # Select next link using XOR/CNOT logic
            next_link = self.select_next_link(valid_links)
            if next_link and next_link not in self.visited:
                self.recursive_crawl(next_link, depth + 1)

        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")

    def match_target_words(self, text):
        """Check if any of the target words exist in the text."""
        return any(word in text for word in self.target_words)

    def update_grid(self, content):
        # Light up current position
        self.grid[self.current_position[0]][self.current_position[1]] = 1
        self.display_grid()
        time.sleep(0.5)  # Pause to show changes

        # Perform XOR operation
        self.xor_operation(content)

        # Move to next position
        self.move_position()

    def xor_operation(self, content):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if any(ord(char) & 1 for char in content[i*self.grid_size + j:i*self.grid_size + j + self.grid_size]):
                    self.grid[i][j] ^= 1  # XOR operation
        print("XOR operation performed")
        self.display_grid()
        time.sleep(0.5)  # Pause to show changes

    def cnot_operation(self, control, target):
        if self.grid[control[0]][control[1]] == 1:
            self.grid[target[0]][target[1]] ^= 1  # Flip target if control is 1
        print(f"CNOT operation performed: Control {control}, Target {target}")
        self.display_grid()
        time.sleep(0.5)  # Pause to show changes

    def select_next_link(self, links):
        if not links:
            return None
        
        # Use XOR operation to select initial link index
        xor_sum = sum(sum(row) for row in self.grid)
        link_index = xor_sum % len(links)
        
        # Use CNOT operation to potentially modify the selection
        control = self.current_position
        target = [(xor_sum // self.grid_size) % self.grid_size, xor_sum % self.grid_size]
        self.cnot_operation(control, target)
        
        # If CNOT flipped the target, adjust the link selection
        if self.grid[target[0]][target[1]] == 1:
            link_index = (link_index + 1) % len(links)
        
        return links[link_index]

    def move_position(self):
        """Move to the next position on the grid."""
        self.current_position[1] += 1
        if self.current_position[1] >= self.grid_size:
            self.current_position[1] = 0
            self.current_position[0] += 1
        if self.current_position[0] >= self.grid_size:
            self.current_position = [0, 0]

    def display_grid(self):
        """Display the current state of the grid."""
        for row in self.grid:
            print(' '.join(['○' if cell else '●' for cell in row]))
        print()

# Usage Example:
target_keywords = ["quantum", "new", "novel"]
crawler = XOR_CNOT_OUTCrawle(sys.argv[1], target_words=target_keywords)
crawler.crawl()
