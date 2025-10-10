from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Chatbot import ChatBot
from Backend.Model import FirstLayerDMM

app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_index():
    return send_from_directory('Web-Frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('Web-Frontend', path)

@app.route('/api/ask', methods=['POST'])
def handle_query():
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "No query provided."}), 400
    
    try:
        decision_list = FirstLayerDMM(query)
        print(f"Decision for web query '{query}': {decision_list}")
        
        is_automation_task = any(d.startswith(("open", "close", "play", "system")) for d in decision_list)
        if is_automation_task:
            response = "This feature is only available in the downloadable desktop application. It allows me to interact with your local system."
            return jsonify({"response": response})
        
        is_image_task = any("generate image" in d for d in decision_list)
        if is_image_task:
            response = f"Image generation is an exclusive feature available only in the JARVIS desktop application. Please download the app to experience this and other advanced automation capabilities!"
            return jsonify({"response": response})
        
        is_realtime_task = any(d.startswith("realtime") for d in decision_list)
        if is_realtime_task:
            clean_query = " ".join(decision_list[0].split()[1:])
            response = RealtimeSearchEngine(clean_query)
            return jsonify({"response": response})
        
        clean_query = " ".join(decision_list[0].split()[1:])
        response = ChatBot(clean_query)
        return jsonify({"response": response})
    
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({"error": "An internal error occurred."}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)