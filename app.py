from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# -------------------- Config --------------------
API_URL = "" #endpoint
LOGIN_ID = "" # Add your login(email) ID here
PASSWORD = ""  # Add your password here
ORG_ID = "" # Add your org ID here

# Payload to fetch all available tasks
ALL_TASKS_PAYLOAD = {
    "data": [
        {
            "models": ["taskType"],
            "columns": {
                "name": "taskType.name",
                "id": "taskType.id"
            },
            "filter": "{$taskType.mobileProcessId} = '__sys__standard_mobile_workflow'",
            "distinct": True,
            "getCount": True
        }
    ]
}

# -------------------- HTML Template --------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Task Fetcher</title>
    <script>
        // Toggle Select All checkboxes
        function toggleSelectAll(source) {
            let checkboxes = document.getElementsByName('task_ids');
            for (let i = 0; i < checkboxes.length; i++) {
                checkboxes[i].checked = source.checked;
            }
        }

        // Copy table to clipboard (Excel friendly)
        function copyTableToClipboard() {
            let table = document.getElementById("taskTable");
            if (!table) {
                alert("No table to copy!");
                return;
            }

            let range = document.createRange();
            range.selectNode(table);
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);

            try {
                document.execCommand('copy');
                alert("Table copied! You can now paste it into Excel.");
            } catch (err) {
                alert("Failed to copy table: " + err);
            }

            window.getSelection().removeAllRanges();
        }
    </script>
</head>
<body>
    <h2>Fetch Task Definition</h2>
    <form method="post">
        {% if all_tasks %}
            <label><input type="checkbox" onclick="toggleSelectAll(this)"> Select All</label><br><br>
            {% for task in all_tasks %}
                <input type="checkbox" name="task_ids" value="{{ task.id }}"> {{ task.name }} ({{ task.id }})<br>
            {% endfor %}
        {% else %}
            <p>No tasks found.</p>
        {% endif %}
        <br>
        <input type="submit" value="Fetch Definition">
    </form>

    {% if response %}
        <h3>Task Components:</h3>
        <button onclick="copyTableToClipboard()">Copy Table to Excel</button><br><br>
        {{ response|safe }}
    {% endif %}
</body>
</html>
"""

# -------------------- Functions --------------------
def get_all_tasks():
    headers = {
        "Content-Type": "application/json",
        "loginId": LOGIN_ID,
        "password": PASSWORD,
        "orgId": ORG_ID
    }
    try:
        res = requests.post(API_URL, json=ALL_TASKS_PAYLOAD, headers=headers)
        if res.ok:
            data = res.json()
            tasks = []
            for row in data.get("data", []):
                task_id = row.get("id")
                task_name = row.get("name", "Unnamed Task")
                if task_id:
                    tasks.append({"id": task_id, "name": task_name})
            return tasks
        return []
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []

def parse_task_response(response_json):
    rows = []

    if "data" not in response_json:
        return rows

    def parse_components(components, task_type_title, subpages=None):
        for comp in components:
            comp_type = comp.get("type", "-")
            title = comp.get("heading") or comp.get("title") or "-"
            key_in_taskbuilder = comp.get("id") or (comp.get("value", "").split(".")[-1] if comp.get("value") else "-")

            rows.append({
                "TaskType": task_type_title,
                "Component": comp_type,
                "Title": title,
                "Key in TaskBuilder": key_in_taskbuilder
            })

            if comp_type.lower() == "card" and subpages:
                sub_page_data = subpages.get(key_in_taskbuilder, [])
                for sp in sub_page_data:
                    parse_components(sp.get("components", []), task_type_title, subpages)

    for task in response_json["data"]:
        task_builder_config = task.get("taskBuilderConfig", {}).get("taskBuilderConfig", {})
        dynamic_pages = task_builder_config.get("dynamicPages", {})
        subpages = task_builder_config.get("subPages", {})

        for page_id, page_data in dynamic_pages.items():
            task_type_title = "Residential Install" if page_data.get("title") == "Check In" else page_data.get("title", "Unnamed Task")
            cols = page_data.get("cols", [])
            for col in cols:
                body_items = col.get("body", [])
                parse_components(body_items, task_type_title, subpages)

    return rows

# -------------------- Flask Route --------------------
@app.route("/", methods=["GET", "POST"])
def fetch_task():
    response_html = None
    all_tasks = get_all_tasks()

    if request.method == "POST":
        task_ids = request.form.getlist("task_ids")
        if task_ids:
            payload = {
                "data": [
                    {
                        "models": ["TaskType"],
                        "columns": {
                            "taskBuilderConfig": "TaskType.taskBuilderConfig",
                            "id": "TaskType.id"
                        },
                        "distinct": True,
                        "inputs": {"taskIds": task_ids},
                        "filter": "{$id} in {@taskIds}",
                        "getCount": True
                    }
                ]
            }
            headers = {
                "Content-Type": "application/json",
                "loginId": LOGIN_ID,
                "password": PASSWORD,
                "orgId": ORG_ID
            }
            try:
                res = requests.post(API_URL, json=payload, headers=headers)
                if res.headers.get("Content-Type", "").startswith("application/json"):
                    res_json = res.json()
                    table_rows = parse_task_response(res_json)

                    if table_rows:
                        # Added id="taskTable" for copy functionality
                        table_html = "<table id='taskTable' border='1' cellpadding='5' cellspacing='0'>"
                        table_html += "<tr><th>Task Type</th><th>Component</th><th>Title</th><th>Key in TaskBuilder</th></tr>"
                        for row in table_rows:
                            table_html += f"<tr><td>{row['TaskType']}</td><td>{row['Component']}</td><td>{row['Title']}</td><td>{row['Key in TaskBuilder']}</td></tr>"
                        table_html += "</table>"
                    else:
                        table_html = "No components found in selected tasks."
                    response_html = table_html
                else:
                    response_html = res.text
            except Exception as e:
                response_html = f"Error: {str(e)}"

    return render_template_string(HTML_TEMPLATE, response=response_html, all_tasks=all_tasks)

# -------------------- Run App --------------------
if __name__ == "__main__":
    app.run(debug=True)
