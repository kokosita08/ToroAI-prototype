# This file creates the API for TOROAI - frontend and backend both 
# Workflow of the file : frontend sends question -> API receives question -> TOROAI creates answer -> API sends answer back

from flask import Flask 
from flask import request 
from flask import jsonify 
from flask_cors import CORS 

from backend.src.generation import generate_answer

# create the Flask application 
app = Flask(__name__)

# allow the frontend to send request to this API 
CORS(app)

# HOME ROUTE - this route is only used to check if the backend is running
@app.route("/", methods = ["GET"])
def home():
    return jsonify({"message":"ToroAI API is running"})

# Chat route - frontend will send the user's request here 

@app.route("/chat", methods = ["POST"])
def chat():

    data = request.get_json()             #get the JSON data sent by the frontend 

    if data is None:
        return jsonify({"error":"No data was received"}), 400 
    if "question" not in data:
        return jsonify({"error":"Question is required"}), 400

    question = data["question"]          # get the user's question

    result = generate_answer(question)    # send the question to toroai's RAG system 

    answer= result["answer"]            # get the final answer

    sources = result["sources"]         # get the source link 

    # send the answer and source back to the frontend 
    return jsonify({"answer":answer , "sources": sources})


# start API server 

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 8080, debug = True)


