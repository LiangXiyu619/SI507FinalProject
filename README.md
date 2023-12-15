# Required Python Packages:
 - requests
 - Pillow (PIL)

# Apply API Keys:

## Yelp API Key

Open `data_yelp.py` and replace the value of `API_KEY` in Line 1 with your Yelp API key.

## Google Maps API Key

Open `data_map.py` and replace the value of `API_KEY` in Line 1 with your Google Maps API key.

# Interact with the Program:

1. Put `cache.json` and `tree.py` under the same directory.
2. Run `tree.py` in the terminal.
3. Follow the instructions in the terminal to interact with the program.

# Data Structure

The data structure of this project is a K-D tree. Each node in the tree represents a business. Business attributes like name, price and address are stored in the node. The nodes in the tree are sorted by price, ratings, distance and traveling time.

The data is collected by running data_yelp.py then data_map.py. It is stored in cache.json. tree.py reads cache.json, and constructs the K-D tree.