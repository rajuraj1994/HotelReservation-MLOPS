import os 
import pandas as pd
import numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from utils.common_functions import read_yaml, load_data
from config.paths_config import *
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import sys


logger = get_logger(__name__)

class DataProcessor:

    def __init__(self,train_path,test_path,processed_dir,config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir
        self.config = read_yaml(config_path)

        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

    def preprocess_data(self,df):
        try:
            logger.info("Starting data preprocessing")
            logger.info("Dropping the columns")
            df.drop(columns=['Booking_ID'], inplace=True)
            df.drop_duplicates(inplace=True)

            cat_cols =  self.config["data_preprocessing"]["categorical_columns"]
            num_cols = self.config["data_preprocessing"]["numerical_columns"]

            logger.info("Encoding categorical columns using Label Encoding")
            label_encoder = LabelEncoder()
            mappings = {}

            for col in cat_cols:
                df[col] = label_encoder.fit_transform(df[col])
                mappings[col] = {label: code for label, code in zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_))}

            logger.info("Label Mappings are : ")
            for col, mapping in mappings.items():
                logger.info(f"{col} : {mapping}")
            
            logger.info("Doing skewness Handling")
            skew_thresholsd = self.config["data_preprocessing"]["skewness_threshold"]
            skewness = df[num_cols].apply(lambda x: x.skew())

            for column in skewness[skewness > skew_thresholsd].index:
                df[column] = np.log1p(df[column])

            logger.info("Data preprocessing completed successfully")
            return df


           
        except Exception as e:
            logger.error(f"Error during data preprocessing - {str(e)}")
            raise CustomException(f"Error during data preprocessing - {str(e)}", sys)

    def balance_data(self,df):
        try:
            logger.info("Starting data balancing using SMOTE")
            X = df.drop(columns=['booking_status'])
            y = df['booking_status']

            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X, y)

            balanced_df = pd.DataFrame(X_resampled, columns=X.columns)
            balanced_df['booking_status'] = y_resampled

            logger.info("Data balancing completed successfully")
            return balanced_df
        
        except Exception as e:
            logger.error(f"Error during data balancing - {str(e)}")
            raise CustomException(f"Error during data balancing - {str(e)}", sys)
        
    def select_features(self,df):
        try:
            logger.info("Starting our Feature selection step")

            X = df.drop(columns='booking_status')
            y = df["booking_status"]

            model =  RandomForestClassifier(random_state=42)
            model.fit(X,y)

            feature_importance = model.feature_importances_

            feature_importance_df = pd.DataFrame({
                        'feature':X.columns,
                        'importance':feature_importance
                            })
            top_features_importance_df = feature_importance_df.sort_values(by="importance" , ascending=False)

            num_features_to_select = self.config["data_preprocessing"]["no_of_features"]

            top_10_features = top_features_importance_df["feature"].head(num_features_to_select).values

            logger.info(f"Features selected : {top_10_features}")

            top_10_df = df[top_10_features.tolist() + ["booking_status"]]

            logger.info("Feature slection completed sucesfully")

            return top_10_df
        
        except Exception as e:
            logger.error(f"Error during feature selection step {e}")
            raise CustomException("Error while feature selection", e)
    
    def save_processed_data(self,df,file_path):
        try:
            logger.info(f"Saving processed data to path: {file_path}")
            df.to_csv(file_path, index=False)
            logger.info(f"Processed data saved successfully to path: {file_path}")
        except Exception as e:
            logger.error(f"Error saving processed data to path: {file_path} - {str(e)}")
            raise CustomException(f"Error saving processed data to path: {file_path} - {str(e)}", sys)
    
    def process(self):
        try:
            logger.info("Loading data from raw data paths")
            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)
            logger.info("Preprocessing the training data")
            processed_train_df = self.preprocess_data(train_df)
            logger.info("Preprocessing the test data")
            preprocessed_test_df = self.preprocess_data(test_df)
            logger.info("Balancing the training data")
            balanced_train_df = self.balance_data(processed_train_df)
            logger.info("Selecting features from the training data")
            selected_train_df = self.select_features(balanced_train_df)
            logger.info("Saving the processed training data")
            self.save_processed_data(selected_train_df, PROCESSED_TRAIN_FILE_PATH)
            logger.info("Selecting features from the test data")
            selected_test_df = preprocessed_test_df[selected_train_df.columns.drop('booking_status')]
            selected_test_df['booking_status'] = preprocessed_test_df['booking_status']
            logger.info("Saving the processed test data")
            self.save_processed_data(selected_test_df, PROCESSED_TEST_FILE_PATH)
            logger.info("Data processing completed successfully")
            
        except Exception as e:
            logger.error(f"Error during data processing - {str(e)}")
            raise CustomException(f"Error during data processing - {str(e)}", sys)
        


if __name__=="__main__":
    processor = DataProcessor(TRAIN_FILE_PATH,TEST_FILE_PATH,PROCESSED_DIR,CONFIG_PATH)
    processor.process()  