from flask import Flask, render_template, request
from datetime import datetime
import requests


app = Flask(__name__)


@app.route("/")
def index():
    launch_filter = request.args.get("filter", "all")
    launches = organize_launch_data_by_category(fetch_launch_data())
    filtered_launches = launches.get(launch_filter, launches["all"])
    for launch in filtered_launches:
        launch["date_utc"] = format_date(launch["date_utc"])
        launch["date_local"] = format_date(launch["date_local"])
    return render_template("index.html", launches=filtered_launches, filter=launch_filter, count=len(filtered_launches))


@app.route("/launch/<launch_id>")
def launch(launch_id):
    launches = fetch_launch_data()
    launch = next((launch for launch in launches if launch["id"] == launch_id), None)
    launch["date_utc"] = format_date(launch["date_utc"])
    launch["date_local"] = format_date(launch["date_local"])
    if not launch:
        return "Launch not found", 404
    return render_template("launch.html", launch=launch)

def format_date(date_string):
    if date_string:
        if date_string.endswith("Z"):
            dt = datetime.fromisoformat(date_string[:-1])  # Remove Z from the end
        else:
            dt = datetime.fromisoformat(date_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return ""
def fetch_launch_data():
    launch_data = "https://api.spacexdata.com/v5/launches"
    response = requests.get(launch_data)

    return response.json() if response.status_code == 200 else []


def organize_launch_data_by_category(launches):
    successful = list(filter(lambda launch: launch["success"], launches))
    failed = list(filter(lambda launch: not launch["success"], launches))
    upcoming = list(filter(lambda launch: launch["upcoming"], launches))

    return {
        "successful": successful,
        "failed": failed,
        "upcoming": upcoming,
        "all": launches
    }


if __name__ == "__main__":
    app.run(debug=True)
