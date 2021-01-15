def get_graph_params(json_graph):
    """Reads params from json graph

    Args:
        json_graph (dict): graph information

    Returns:
        params
    """
    
    title = json_graph.get("title", "")
    x = json_graph.get("x", [])
    y = json_graph.get("y", [])
    label_x = json_graph.get("labelX", "")
    label_y = json_graph.get("labelY", "")
    chart_type = json_graph.get("chart_type", "bar")
    layout = json_graph.get("layout", {})

    return title, x, y, label_x, label_y, chart_type, layout

def create_json_graph(title, x, y, label_x="x", label_y="y", chart_type="bar", layout={}):
    print()
    
params = get_graph_params({})
print(*params)
create_json_graph(*params)