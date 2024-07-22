from typing import ClassVar, Dict

from pydantic_settings import BaseSettings


# Settings class containing configuration for the application
class Settings(BaseSettings):
    # MongoDB URI for connecting to the MongoDB database
    MONGODB_URI: str = "mongodb+srv://mdalmamunit427:4EsikB9hND59Pvga@jobportal.a2ilieo.mongodb.net/?retryWrites=true&w=majority"
    # Name of the database to be used
    DB_NAME: str = "haraj"
    # URL for the GraphQL API endpoint with specific query parameters
    API_URL: str = "https://graphql.haraj.com.sa/?queryName=search&lang=en&clientId=5PfyC2s3-xlv8-ManX-RCdf-LqhFYr5SkUh3v3&version=N9.0.38%20,%206/28/2024/"

    # GraphQL query for searching posts with optional pagination and city filters
    SEARCH_QUERY: str = '''
    query Search($search: String!, $page: Int, $city: String) {
        search(search: $search, page: $page, city: $city) {
            items {
                id
                title
                postDate
                updateDate
                URL
                bodyHTML
                city
                imagesList
            }
            pageInfo {
                hasNextPage
            }
        }
    }
    '''

    # Dictionary for converting Arabic city names to their Latin script equivalents
    CITY_TRANSLATIONS: Dict[str, str] = {
        'الرياض': 'Riyadh',
        'المنطقة الشرقية': 'Eastern Region',
        'جدة': 'Jeddah',
        'مكة': 'Makkah',
        'ينبع': 'Yanbu',
        'حفر الباطن': 'Hafar Al Batin',
        'المدينة المنورة': 'Madinah',
        'الطائف': 'Taif',
        'تبوك': 'Tabouk',
        'القصيم': 'Qassim',
        'حائل': 'Hail',
        'أبها': 'Abha',
        'عسير': 'Aseer',
        'الباحة': 'Bahah',
        'جازان': 'Jazan',
        'نجران': 'Najran',
        'الجوف': 'Jouf',
        'عرعر': 'Arar',
        'الكويت': 'Kuwait',
        'الإمارات': 'UAE',
        'البحرين': 'Bahrain',
        # Add other cities as required
    }

    # Settings for controlling the request timeout duration
    REQUEST_TIMEOUT: ClassVar[int] = 10  # seconds
    # Maximum number of retry attempts for failed requests
    MAX_RETRIES: ClassVar[int] = 3
    # Delay between retry attempts
    RETRY_DELAY: ClassVar[int] = 5  # seconds
    # Maximum number of concurrent requests allowed
    MAX_CONCURRENT_REQUESTS: ClassVar[int] = 20


# Configuration class to specify the environment file
class Config:
    env_file = ".env"


# Instantiate the Settings class
settings = Settings()
