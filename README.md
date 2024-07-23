# SCPROJECT-

## Backend Script Overview

This Python script serves as the backend for a web scraping and data management system. It's designed to fetch, parse, and store data from an external API, specifically for searching and retrieving posts. Here's how it works and how to integrate it with your front-end:

### Key Features:

1. Asynchronous data fetching from an external API
2. Pagination handling for large datasets
3. Data parsing and storage in a database(Mongo DB)
4. Search functionality with city filtering
5. Background task processing for real-time updates

## Setup

1. Clone the repository:
   git clone https://github.com/yourusername/haraj-scraper.git
   cd haraj-scraper

2. Install dependencies:
   pip install -r requirements.txt

3. Set up environment variables:
   Create a `.env` file in the root directory and add the following:

-`MONGODB_URI`="" -`DB_NAME`="haraj-db"
`API_URL`="https://graphql.haraj.com.sa/?queryName=search&lang=en&clientId=5PfyC2s3-xlv8-ManX-RCdf-LqhFYr5SkUh3v3&version=N9.0.38%20,%206/28/2024/" -`PORT`=8000

## Configuration

The project uses a `config.py` file to manage settings. This file loads environment variables and defines configuration parameters. Here's an overview of the key settings:

### Environment Variables (defined in .env file):

- `MONGODB_URI`: MongoDB connection string
- `DB_NAME`: Name of the MongoDB database
- `API_URL`: URL for the Haraj GraphQL API
- `PORT`: Port number for the FastAPI application (default: 8000)

### Other Important Settings:

- `SEARCH_QUERY`: GraphQL query for searching posts
- `CITY_TRANSLATIONS`: Dictionary for converting Arabic city names to their Latin script equivalents
- `REQUEST_TIMEOUT`: Maximum duration for a request (10 seconds)
- `MAX_RETRIES`: Maximum number of retry attempts for failed requests (3)
- `RETRY_DELAY`: Delay between retry attempts (5 seconds)
- `MAX_CONCURRENT_REQUESTS`: Maximum number of concurrent requests allowed (20)

To modify these settings, you can either update the `.env` file or modify the `config.py` file directly.

## Usage

### Running the script

To start the server:
python main.py

### How It Works:

1. The script fetches data from an API based on search queries and city filters.
2. It stores the fetched data in a database, organizing it into collections.
3. When the front-end requests data, the script searches the local database first.
4. If insufficient data is found, it triggers a background task to fetch more data from the API.

### Integration with Front-end:

To use this backend script with your front-end, you'll need to set up API endpoints that your front-end can call. Here are the main functionalities you should expose:

1. **Search Posts:**

   - Endpoint: `/search`
   - Method: GET
   - Parameters:
     - `query`: Search term
     - `city`: (Optional) City filter
     - `page`: Page number
     - `limit`: Number of results per page
   - This will call the `search_posts_service` function

2. **Get Specific Post:**

   - Endpoint: `/post/<post_id>`
   - Method: GET
   - This will call the `get_post_service` function

3. **Update Database:**
   - Endpoint: `/update`
   - Method: POST
   - This can trigger the `update_all_collections` function to refresh the database

### Front-end Implementation:

1. Use AJAX or Fetch API to make requests to these endpoints.
2. Handle pagination in your UI, making new requests as the user scrolls or clicks through pages.
3. Implement a search form that sends queries to the search endpoint.
4. Create a detailed view page that fetches specific post data using the post ID.

### Example Front-end Code (JavaScript):

```javascript
// Search for posts
async function searchPosts(query, city, page = 1, limit = 20) {
	const response = await fetch(
		`/api/search?query=${query}&city=${city}&page=${page}&limit=${limit}`
	)
	return await response.json()
}

// Get a specific post
async function getPost(postId) {
	const response = await fetch(`/api/post/${postId}`)
	return await response.json()
}

// Update the database (admin function)
async function updateDatabase() {
	const response = await fetch('/api/update', { method: 'POST' })
	return await response.json()
}
```
