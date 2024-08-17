# Haraj.com.sa Scraper Backend

This project is a backend service for scraping and managing data from Haraj.com.sa. It provides an API for searching posts, retrieving specific posts, and updating the database with new data.

## Features

- Asynchronous data fetching from Haraj.com.sa API
- MongoDB integration for data storage
- FastAPI-based RESTful API
- Scheduled background tasks for data updates
- City-based filtering and pagination support

## Prerequisites

- Python 3.7+
- MongoDB
- pip (Python package manager)

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/haraj-scraper.git
   cd haraj-scraper
   ```

2. Create a virtual environment:

   ```
   python -m venv .myenv
   source .myenv/bin/activate  # On Windows use `.myenv\Scripts\activate`
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following content:
   ```
   MONGODB_URI=your_mongodb_connection_string
   DB_NAME=haraj-db
   API_URL=https://graphql.haraj.com.sa/?queryName=search&lang=en&clientId=5PfyC2s3-xlv8-ManX-RCdf-LqhFYr5SkUh3v3&version=N9.0.38%20,%206/28/2024/
   PORT=8000
   ```

## Running Locally

To run the server locally:

```
python main.py
```

The server will start on `http://localhost:8000`.

## API Endpoints

### Root Endpoint

- `GET /`: Root endpoint to check if the server is running

  Example request:

  ```
  curl http://localhost:8000/
  ```

  Example response:

  ```json
  {
  	"message": "The server is running successfully"
  }
  ```

### Search Posts

- `GET /search/`: Search for posts with optional city filtering and pagination

  Example request:

  ```
  curl "http://localhost:8000/search/?query=car&city=Riyadh&page=1&limit=10"
  ```

  Example response (when data is found):

  ```json
  {
  	"posts": [
  		{
  			"id": "140507182",
  			"bodyHTML": "<p>Car for sale in excellent condition...</p>",
  			"title": "2020 Toyota Camry for Sale",
  			"URL": "https://haraj.com.sa/en/11140507182/toyota_camry_2020",
  			"city": "Riyadh",
  			"postDate": "2024-07-23T10:22:23",
  			"updateDate": "2024-07-23T10:22:23",
  			"firstImage": "https://mimg6cdn.haraj.com.sa/userfiles30/2024-07-23/1350x1800_CE6D1043-6A81-44F8-B36B-818BF2E1922C.jpg",
  			"commentCount": 0,
  			"tags": ["car", "toyota", "camry"],
  			"authorUsername": "cardealer123",
  			"price": {
  				"formattedPrice": "50,000 SAR"
  			}
  		}
  		// ... more posts
  	],
  	"is_complete": true,
  	"total_count": 100,
  	"current_page": 1,
  	"total_pages": 10,
  	"has_previous_page": false,
  	"has_next_page": true,
  	"message": "Data successfully retrieved."
  }
  ```

  Example response (when no data is found):

  ```json
  {
  	"posts": [],
  	"is_complete": true,
  	"total_count": 0,
  	"current_page": 1,
  	"total_pages": 0,
  	"has_previous_page": false,
  	"has_next_page": false,
  	"message": "No posts available for this query."
  }
  ```

### Get Specific Post

- `GET /post/{post_id}`: Retrieve a specific post by ID

  Example request:

  ```
  curl http://localhost:8000/post/140507182
  ```

  Example response:

  ```json
  {
  	"id": "140507182",
  	"bodyHTML": "<p>Car for sale in excellent condition...</p>",
  	"title": "2020 Toyota Camry for Sale",
  	"URL": "https://haraj.com.sa/en/11140507182/toyota_camry_2020",
  	"city": "Riyadh",
  	"postDate": "2024-07-23T10:22:23",
  	"updateDate": "2024-07-23T10:22:23",
  	"firstImage": "https://mimg6cdn.haraj.com.sa/userfiles30/2024-07-23/1350x1800_CE6D1043-6A81-44F8-B36B-818BF2E1922C.jpg",
  	"commentCount": 0,
  	"tags": ["car", "toyota", "camry"],
  	"authorUsername": "cardealer123",
  	"price": {
  		"formattedPrice": "50,000 SAR"
  	}
  }
  ```

### Update Database

- `POST /update`: Trigger a manual database update (background task)

  Example request:

  ```
  curl -X POST http://localhost:8000/update
  ```

  Example response:

  ```json
  {
  	"message": "Database update initiated"
  }
  ```

## Deployment

To deploy on a server:

1. Set up a MongoDB instance (e.g., MongoDB Atlas)
2. Clone the repository on your server
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables (see Installation step 4)
5. Run the application using a process manager like PM2 or supervisord:
   ```
   pm2 start main.py --interpreter python3
   ```

## Development

- The project structure is as follows:
  ```
  scrapper/
  ├── main.py
  ├── config.py
  ├── db/
  │   ├── database.py
  │   └── models.py
  └── utils/
      ├── routes.py
      ├── handlers.py
      └── services.py
  ```
- To add new features, extend the `PostService` class in `utils/services.py`
- Add new routes in `utils/routes.py`
- Modify database operations in `db/database.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
