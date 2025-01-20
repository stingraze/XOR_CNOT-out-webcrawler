import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random
import time
import sys

class XOR_CNOT_OUTCrawler:
    def __init__(self, start_url, max_depth=3, grid_size=5):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()
        self.grid_size = grid_size
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        self.current_position = [0, 0]

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

            # Update grid based on page content
            self.update_grid(soup.get_text())

            # Crawl valid links
            for link in valid_links:
                if link not in self.visited:
                    self.recursive_crawl(link, depth + 1)

        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")

    def update_grid(self, content):
        # Light up current position
        self.grid[self.current_position[0]][self.current_position[1]] = 1
        self.display_grid()
        time.sleep(0.5)  # Pause to show changes

        # Decide between XOR and CNOT-like operation
        if random.choice([True, False]):
            self.xor_operation(content)
        else:
            self.cnot_operation()

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

    def cnot_operation(self):
        control = self.current_position
        target = [random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)]
        if self.grid[control[0]][control[1]] == 1:
            self.grid[target[0]][target[1]] ^= 1  # Flip target if control is 1
        print(f"CNOT operation performed: Control {control}, Target {target}")
        self.display_grid()
        time.sleep(0.5)  # Pause to show changes

    def move_position(self):
        self.current_position[1] += 1
        if self.current_position[1] >= self.grid_size:
            self.current_position[1] = 0
            self.current_position[0] += 1
        if self.current_position[0] >= self.grid_size:
            self.current_position = [0, 0]

    def display_grid(self):
        for row in self.grid:
            print(' '.join(['○' if cell else '●' for cell in row]))
        print()

# Usage

crawler =  XOR_CNOT_OUTCrawler(sys.argv[1])
crawler.crawl()
