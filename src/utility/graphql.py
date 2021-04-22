import requests
from src.utility.logger import logger

def fetch_dp_charts_driver(region_endpoint, vin):

    query = f"""
        {{
        fetchAnalyticResultsDriver(id:"{vin}"){{
            title
            type
            graph
        }}
        }}
        """
    try:
        request = requests.post(
            'http://localhost:4001/graphql', json={'query': query})
    except Exception as e:
        logger.error(f'Error fetching data from GraphQL: {str(e)}')
        return []

    if request.status_code == 200:
        response = request.json()["data"]["fetchAnalyticResultsDriver"]
        return response if response else []
    else:
        logger.error("Query failed to run by returning code of {}. {}".format(
            request.status_code, query))
        return []

def fetch_dp_charts(region_endpoint):

    query = """
        {
        fetchAnalyticResults{
            title
            type
            graph
        }
        }
        """

    try:
        request = requests.post(
        'http://localhost:4001/graphql', json={'query': query})
    except Exception as e:
        logger.error(f'Error fetching data from GraphQL: {str(e)}')
        return []

    if request.status_code == 200:
        response = request.json()["data"]["fetchAnalyticResults"]
        return response if response else []
    else:
        logger.error("Query failed to run by returning code of {}. {}".format(
            request.status_code, query))
        return []
