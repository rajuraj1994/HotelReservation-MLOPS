import os
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]
        self.mongodb_url = self.config["mongodb_url"]
        self.database_name = self.config["database_name"]
        self.collection_name = self.config["collection_name"]
        self.train_test_ratio = self.config["train_ratio"]

        # Ensure directories exist
        os.makedirs(os.path.dirname(TRAIN_FILE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(TEST_FILE_PATH), exist_ok=True)

    def upload_data_to_mongodb(self):
        """
        Reads the local CSV artifact and pushes it to MongoDB Atlas.
        """
        try:
            logger.info(f"Reading local artifact from {RAW_FILE_PATH}")
            df = pd.read_csv(RAW_FILE_PATH)
            
            # Convert DataFrame to a list of dictionaries (JSON format)
            records = df.to_dict(orient="records")

            # Connect and Upload
            client = MongoClient(self.mongodb_url)
            database = client[self.database_name]
            collection = database[self.collection_name]

            # Clear existing data to avoid duplicates (Optional)
            collection.delete_many({}) 
            
            collection.insert_many(records)
            logger.info(f"Successfully uploaded {len(records)} records to MongoDB Atlas.")

        except Exception as e:
            logger.error("Error while uploading data to MongoDB")
            raise CustomException("Failed to upload local artifact to Database", e)

    def split_and_save_artifacts(self):
        """
        Splits the local raw artifact into train and test sets.
        """
        try:
            logger.info("Starting the train-test split process")
            data = pd.read_csv(RAW_FILE_PATH)
            
            train_data, test_data = train_test_split(
                data, 
                test_size=1 - self.train_test_ratio, 
                random_state=42
            )

            # Save to specific artifact paths
            train_data.to_csv(TRAIN_FILE_PATH, index=False)
            test_data.to_csv(TEST_FILE_PATH, index=False)

            logger.info(f"Train data saved at: {TRAIN_FILE_PATH}")
            logger.info(f"Test data saved at: {TEST_FILE_PATH}")
        
        except Exception as e:
            logger.error("Error during data splitting")
            raise CustomException("Failed to create train/test artifacts", e)
        
    def run(self):
        try:
            logger.info("Initiating Data Ingestion: Artifact to MongoDB & Split")

            # 1. Sync local data to Cloud DB
            self.upload_data_to_mongodb()
            
            # 2. Split for model consumption
            self.split_and_save_artifacts()

            logger.info("Data Ingestion Pipeline completed successfully")
        
        except CustomException as ce:
            logger.error(f"Process Failed: {str(ce)}")

if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()