import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import numpy as np
import sys
import random
#Created using ChatGPT o1 mini 
#(C)Tsubasa Kato - Inspire Search Corp.
#https://www.inspiresearch.io/en
# -----------------------------
# Dummy state setup using a 2D grid
# -----------------------------
Lx, Ly = 5, 5

def initialize_state(Lx, Ly):
    """Initialize the state as an Lx x Ly grid of zeros."""
    state = np.zeros((Lx, Ly), dtype=int)
    print("Initial state:")
    print(state)
    return state

def apply_cnot_lights_out(state, pos):
    """
    Apply a "lights out" style toggle (a variation of a CNOT) on the state.
    
    The cell at `pos` and its direct neighbors (up, down, left, right) are flipped.
    This function prints the details of the operation.
    """
    i, j = pos
    new_state = state.copy()
    
    # Define the positions to toggle: the cell itself and its direct neighbors.
    positions = [(i, j), (i-1, j), (i+1, j), (i, j-1), (i, j+1)]
    print(f"\nApplying CNOT at position {pos}:")
    for x, y in positions:
        if 0 <= x < Lx and 0 <= y < Ly:
            before = new_state[x, y]
            new_state[x, y] = 1 - new_state[x, y]  # Flip the bit.
            after = new_state[x, y]
            print(f"  Toggled cell ({x}, {y}): {before} -> {after}")
    print("State after this CNOT operation:")
    print(new_state)
    return new_state

def evolve_state(state, dt):
    """
    Evolve the state by applying a CNOT style operation at a random position.
    
    The parameter dt is kept for interface compatibility though it is unused in this dummy evolution.
    """
    control_pos = (random.randint(0, Lx-1), random.randint(0, Ly-1))
    print(f"\nEvolving state by applying CNOT at random position {control_pos}.")
    new_state = apply_cnot_lights_out(state, control_pos)
    return new_state

# Global variable to remember last index chosen
last_chosen_index = None

def select_next_url(state, control_matrix, available_urls):
    """
    Use the current state to decide which URL to choose next.
    
    The current state is combined with a control matrix via logical XOR,
    then converted to a binary string and interpreted as an integer.
    This integer (modulo the number of available URLs) determines the candidate index.
    
    If the candidate index is the same as the last selected, additional toggling is applied.
    """
    global last_chosen_index
    
    try:
        # Combine state and control matrix using XOR.
        combined_state = np.logical_xor(state, control_matrix).astype(int)
        binary_string = ''.join(map(str, combined_state.flatten()))
        candidate_index = int(binary_string, 2) % len(available_urls)
        print(f"\nInitial candidate index based on state XOR control: {candidate_index}")
        
        # If candidate equals the previous index, apply additional CNOT toggles until it changes.
        attempt = 0
        while candidate_index == last_chosen_index and attempt < 5:
            print("Candidate index is the same as the last chosen index. Applying additional CNOT toggle...")
            # Apply an extra CNOT toggle at a random location.
            control_pos = (random.randint(0, Lx-1), random.randint(0, Ly-1))
            state = apply_cnot_lights_out(state, control_pos)
            
            # Recompute the candidate index.
            combined_state = np.logical_xor(state, control_matrix).astype(int)
            binary_string = ''.join(map(str, combined_state.flatten()))
            candidate_index = int(binary_string, 2) % len(available_urls)
            print(f"New candidate index after additional toggle: {candidate_index}")
            attempt += 1
        
        last_chosen_index = candidate_index
        print(f"Final selected candidate index: {candidate_index}")
        return available_urls[candidate_index], state
    except Exception as e:
        print(f"Error in select_next_url: {e}")
        return None, state

# -----------------------------
# Crawler function
# -----------------------------
def crawl_website(start_url, max_depth=3):
    visited = set()
    dt = 0.1  # dummy time step
    global last_chosen_index
    last_chosen_index = None

    def recursive_crawl(current_url, depth, state):
        if depth > max_depth:
            print(f"\nMaximum depth {max_depth} reached.")
            return state
        if current_url in visited:
            print(f"\nAlready visited: {current_url}")
            return state

        visited.add(current_url)
        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()  # Raise an error for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"\nCrawling (Depth {depth}): {current_url}")

            # Extract links that start with the same base URL
            links = soup.find_all('a', href=True)
            available_urls = [urljoin(current_url, link['href'])
                              for link in links
                              if urljoin(current_url, link['href']).startswith(start_url)]

            if available_urls:
                # Evolve the state using a CNOT toggle
                state = evolve_state(state, dt)

                # Use decision logic with the current state and control matrix to choose next URL.
                next_url, state = select_next_url(state, control_matrix, available_urls)
                
                if next_url:
                    print(f"Selected next URL (index {last_chosen_index}): {next_url}")
                    state = recursive_crawl(next_url, depth + 1, state)
                else:
                    print("No valid next URL selected.")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error for {current_url}: {req_err}")
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
        time.sleep(1)
        return state

    recursive_crawl(start_url, 0, psi)

# -----------------------------
# Global initialization
# -----------------------------
print("Using a dummy state with CNOT evolution.")
control_matrix = np.random.randint(0, 2, size=(Lx, Ly))
print("Control Matrix:")
print(control_matrix)
print("\nInitializing state...")
try:
    psi = initialize_state(Lx, Ly)
except Exception as e:
    print(f"Error initializing state: {e}")
    sys.exit(1)

# -----------------------------
# Main entry point
# -----------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crawler-toric5.py <start_url>")
        sys.exit(1)
    
    start_url = sys.argv[1]
    print("\nStarting crawl:")
    crawl_website(start_url, max_depth=15)
