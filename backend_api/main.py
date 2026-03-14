from data_system.engine import DataSystemEngine

data_engine = DataSystemEngine()

# Giả sử Admin vừa đóng cửa ga Shibuya [cite: 58]
data_engine.add_event({
    "type": "station_closed",
    "target": "Shibuya",
    "duration": "2 hours"
})

def get_data_for_ai():
    clean_json_graph = data_engine.get_refined_graph()

    return clean_json_graph