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

- `GET /`: Root endpoint to check if the server is running
- `GET /search/`: Search for posts with optional city filtering and pagination
- `GET /post/{post_id}`: Retrieve a specific post by ID
- `POST /update`: Trigger a manual database update (background task)

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
