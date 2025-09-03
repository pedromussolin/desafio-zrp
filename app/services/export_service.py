from flask import current_app
import boto3
import pandas as pd
from app.models import Operation

class ExportService:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = current_app.config['S3_BUCKET_NAME']

    def export_operations(self, operations):
        if not operations:
            return None

        # Convert operations to DataFrame
        df = pd.DataFrame([op.to_dict() for op in operations])
        
        # Create a CSV file from the DataFrame
        csv_file_path = '/tmp/operations_export.csv'
        df.to_csv(csv_file_path, index=False)

        # Upload the CSV file to S3
        self.upload_to_s3(csv_file_path)

        return csv_file_path

    def upload_to_s3(self, file_path):
        with open(file_path, 'rb') as data:
            self.s3_client.upload_fileobj(data, self.bucket_name, 'exports/operations_export.csv')