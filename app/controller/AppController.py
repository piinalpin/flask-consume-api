from app import app
from flask import request, render_template
from app.constant import RequestMethod
import pandas as pd
import requests
import os
pd.set_option('display.max_colwidth', -1)

# Define HOST API
host = "http://localhost:5000"


@app.route("/", methods=RequestMethod.GET)
def index():
    return render_template("index.html")


@app.route("/search", methods=RequestMethod.GET_POST)
def search():
    # Define list untuk menampung response dari API
    queries = list()
    details = list()

    # Define request by None
    req = None
    # Jika menggunakan 1 Query
    if request.method == "GET":
        if "q" in request.args:
            if request.args["q"] != "":
                # Define endpoint http://localhost:5000/search?q=bla bla bla
                endpoint = host + "/search?q=" + request.args["q"]
                req = requests.get(endpoint)
            else:
                return "ERROR"
        else:
            return "ERROR"

    # Jika menggunakan Query dari file Excel
    elif request.method == "POST":
        if "files" in request.files:
            # Define endpoint http://localhost:5000/search
            endpoint = host + "/search"
            file = request.files["files"]
            file.save(os.path.join("tmp", "queries.xlsx")) # Save file upload to tmp/
            # Define request files for POST data
            files = {"files": ("queries.xlsx", open("tmp/queries.xlsx", "rb"), 'application/vnd.ms-excel', {'Expires': '0'})}
            req = requests.post(endpoint, files=files)
        else:
            return "ERROR"

    # Process JSON Response to DataFrame
    for query in req.json():
        if "query" in query:
            queries.append(query["query"])
            judul = list()
            pembimbing = list()
            for detail in query["details"]:
                # Get judul and pembimbing to append list
                judul.append(detail["judul"])
                pembimbing.append(detail["pembimbing"])
            # Create dataframe from judul and pembimbing
            df = pd.DataFrame([judul, pembimbing]).T
            df.columns = ["Judul", "Pembimbing"]
            details.append(df)
        else:
            continue
    return render_template("result.html", queries=queries, details=details, n=len(queries))