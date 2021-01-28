from graphqlclient import GraphQLClient
from src.utility import dict_tools
client = GraphQLClient('http://localhost:4000/graphql')

# Provide a GraphQL query
result = client.execute(
    """
query{
  getAnalysis{
    _id
    label
    graphs{
      type
      jsonGraph
    }
  }
}
"""
)

print(type(result))
print(dict_tools.load_json_to_dict(result))
print(dict_tools.load_json_to_dict(result)["data"])
print(dict_tools.load_json_to_dict(result)["data"]["getAnalysis"])