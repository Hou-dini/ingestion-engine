import json
try:
    from google.cloud import storage
except Exception:  # pragma: no cover - optional dependency
    storage = None
from typing import List, Any, Optional, cast
from dataclasses import asdict
from datetime import datetime

from ..core.models import Post
from config.settings import load_settings
import os

# This file requires the 'google-cloud-storage' library.
# You would install it with 'pip install google-cloud-storage'.

class GCSClient:
    """
    A client for interacting with Google Cloud Storage.
    
    This class handles the connection, authentication, and I/O operations
    for saving and loading data from a specified GCS bucket.
    """
    def __init__(self, bucket_name: str):
        """
        Initializes the GCS client with the bucket name.

        Args:
            bucket_name: The name of the GCS bucket to use.
        """
        # Assign instance attributes inside the constructor scope.
        self.bucket_name: str = bucket_name
        # Use Any for external google types to avoid requiring stubs in the project.
        self.client: Optional[Any] = None  # google.cloud.storage.Client
        self.bucket: Optional[Any] = None  # google.cloud.storage.Bucket

    def authenticate(self):
        """
        Authenticates with Google Cloud Storage.
        
        This method uses application default credentials, which is a standard
        way to authenticate in Google Cloud environments. The method will
        automatically find credentials from the environment.
        """
        try:
            # If the optional google-cloud-storage package isn't installed, don't
            # attempt to authenticate. This makes the client safe to import
            # in environments where the dependency is not available (eg. local
            # dev without GCS access).
            if storage is None:
                print("google-cloud-storage package not found; skipping GCS authentication.")
                self.client = None
                self.bucket = None
                return

            # Allow explicit credentials file via settings without overwriting existing env var
            settings = load_settings()
            cred_path = settings.GCS_CREDENTIALS_JSON
            if cred_path:
                # Only set GOOGLE_APPLICATION_CREDENTIALS if not already set and file exists
                if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS') and os.path.isfile(cred_path):
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_path

            # cast to Any so type checkers don't require Google Cloud type stubs
            client = cast(Any, storage.Client())
            if client is not None:
                self.client = client
                # client is a real object here, so calling bucket is safe.
                self.bucket = cast(Any, client.bucket(self.bucket_name))
            else:
                self.client = None
                self.bucket = None
            print(f"Successfully authenticated and connected to GCS bucket: {self.bucket_name}")
        except Exception as e:
            print(f"Failed to authenticate with GCS. Check your credentials. Error: {e}")
            self.client = None
            self.bucket = None

    def save_posts_as_json(self, posts: List[Post], filename: str) -> None:
        """
        Serializes a list of Post objects to a JSON file and saves it to GCS.
        
        Args:
            posts: A list of Post objects to be saved.
            filename: The name of the file to save in the GCS bucket.
        """
        # Be explicit about None checks so static analyzers know `bucket` is not None.
        if self.bucket is None:
            print("GCS client is not authenticated. Cannot save data.")
            return

        # Localize for clarity and to help type checkers understand the value is non-None.
        bucket = self.bucket

        # We need to serialize the dataclass objects into a JSON-friendly format.
        # The `asdict` function from the `dataclasses` module is perfect for this.
        posts_data = [asdict(post) for post in posts]
        
        # We need to handle datetime objects, as they aren't directly serializable to JSON.
        # This function will convert them to ISO 8601 strings.
        def json_encoder(obj: object) -> str:
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        try:
            json_string = json.dumps(posts_data, indent=4, default=json_encoder)
            
            blob = bucket.blob(filename)
            blob.upload_from_string(json_string, content_type='application/json')
            
            print(f"Successfully saved {len(posts)} posts to '{filename}' in GCS.")
        except Exception as e:
            print(f"Failed to save data to GCS. Error: {e}")

    def load_posts_from_json(self, filename: str) -> List[Post]:
        """
        Loads a JSON file from GCS and deserializes it into a list of Post objects.
        
        Args:
            filename: The name of the file to load from the GCS bucket.
            
        Returns:
            A list of Post objects, or an empty list if an error occurs.
        """
        # See note in save_posts_as_json: make the None check explicit.
        if self.bucket is None:
            print("GCS client is not authenticated. Cannot load data.")
            return []

        bucket = self.bucket

        try:
            blob = bucket.blob(filename)
            json_string = blob.download_as_text()
            posts_data = json.loads(json_string)

            # We need to deserialize the JSON data back into our Post objects.
            # This is the reverse of the serialization process.
            posts = []
            for item in posts_data:
                # We need to convert the datetime string back to a datetime object.
                if 'created_at' in item and item['created_at']:
                    item['created_at'] = datetime.fromisoformat(item['created_at'])
                if 'ingested_at' in item and item['ingested_at']:
                    item['ingested_at'] = datetime.fromisoformat(item['ingested_at'])
                
                # The **item syntax "unpacks" the dictionary into keyword arguments
                # for the Post constructor. This is a very powerful Python feature.
                posts.append(Post(**item))
            
            print(f"Successfully loaded {len(posts)} posts from '{filename}' in GCS.")
            return posts
        except Exception as e:
            print(f"Failed to load data from GCS. Error: {e}")
            return []
