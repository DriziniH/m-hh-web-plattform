from graphqlclient import GraphQLClient

from src.utility.logger import logger
from src.utility import dict_tools

def fetchAnalysisResults():
    graphql_client = GraphQLClient('http://localhost:4000/graphql')
    result = graphql_client.execute(
        """
    query{
        fetchAnalysis{
            _id
            label
            graphs{
                type
                title
                chartType
                jsonGraph
            }
        }
    }
    """
    )

    try: 
        result = dict_tools.load_json_to_dict(result)
        return result["data"]["fetchAnalysis"]
    except Exception as e:
        logger.error(f'Error fetching analysis results: {str(e)}')

