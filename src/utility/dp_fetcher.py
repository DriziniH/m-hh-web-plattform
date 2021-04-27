import boto3
from boto3.session import Session
import requests

from src.utility.logger import logger


def fetch_appsync_analysis(region, url):
    """Fetches all analytic results from the AppSync endpoint of the given region

    Args:
        region (String): AWS Region
        url (String): Gateway URL with region endpoint

    Returns:
        analytic_results (dict): Analytic results of the region
    """

    appsync_client = boto3.client('appsync')

    try:
        appsync_client = boto3.client("appsync", region_name=region)
        session = boto3.setup_default_session()

        query = """
            query fetchAnalysisDM {
                data {
                    x
                    y
                    type
                }
                layout {
                    title
                    labelX
                    labelY
                }
        }}"""
        response = session.request(
            url="https://1k41amyped.execute-api.eu-central-1.amazonaws.com/eu", method="POST", json={"query": query})
        return response.text["data"]

    except Exception as e:
        logger.error(
            f"Error while fetching analytic data from region {region}: ", str(e))
        return []


def fetch_dl_files_formatted(region):
    """Fetches and formats all tables from the glue catalog for the given region

    Args:
        region (String): AWS region

    Returns:
        tables (list): List of tables as formatted dicts
    """

    tables = []

    try:
        glue_client = boto3.client("glue", region_name=region)
        response_databases = glue_client.get_databases()

        for response_database in response_databases["DatabaseList"]:
            response_tables = glue_client.get_tables(
                DatabaseName=response_database["Name"])
            for response_table in response_tables["TableList"]:
                try:
                    table = {
                        "name": response_table.get("Name", "Not available"),
                        "description": response_table.get("Description", "Not available"),
                        "location": response_table["StorageDescriptor"].get("Location", "Not available"),
                        "format": format_types.get(response_table["StorageDescriptor"]["SerdeInfo"].get("SerializationLibrary", "Not available"), "Not available")
                    }
                    path = table["location"]+table["name"]+"."+table["format"]
                    table.update({"path": path})
                    tables.append(table)
                except Exception as e:
                    logger.error(
                        f"Error reading table {response_table['Name']} from glue: {str(e)}.")
                    logger.error("Continuing with next table")
        return tables

    except Exception as e:
        logger.error(
            f"Unexpected error while retrieving glue files for region {region}: ", str(e))
        return []


format_types = {
    "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe": "parquet",
    "org.apache.hadoop.hive.serde2.OpenCSVSerde": "csv",
    "org.apache.hadoop.hive.serde2.avro.AvroSerDe": "avro",
    "org.apache.hadoop.hive.ql.io.orc.OrcSerde": "orc",
    "org.openx.data.jsonserde.JsonSerDe": "json"
}


def create_download_link(location, region):
    s3_client = boto3.client('s3',region_name=region)

    location = location.replace("s3://", "")
    bucket = location.split("/")[0]
    key = location.replace(bucket + "/", "")

    try:
        download_link = s3_client.generate_presigned_url('get_object',
                                                         Params={
                                                             'Bucket': bucket, 'Key': key},
                                                         ExpiresIn=60)
        return download_link
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
