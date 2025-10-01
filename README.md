# Extract Task Keys

A Flask-based web application designed to fetch task definitions from a specified API and display the task components in a structured, easily manageable table. A key feature is the "Copy Table to Excel" button, which simplifies data transfer for spreadsheet analysis and reporting.

---

## ✨ Features

* **API Integration:** Securely fetch all available task definitions from the API.
* **Structured Display:** Present task components in a clean, interactive HTML table.
* **Excel Ready:** Easily copy the entire task table to the clipboard for direct pasting into Microsoft Excel or other spreadsheet programs.
* **Selection Control:** Users can select individual tasks or use a convenient "**Select All**" option.

---

## 🛠️ Dependencies

This project requires the following to run:

* **Python 3.x**
* **Flask** (for the web framework)
* **requests** (for API communication)

The required Python packages are listed in `requirements.txt`.

---

## ⚙️ Setup Instructions

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <repository-folder>
```
### 2. Create a Virtual Environment
It's best practice to use a virtual environment to manage dependencies.
```
python -m venv venv
```
### 3. Activate the Virtual Environment
Windows:
```
venv\Scripts\activate
```
Linux / macOS:
```
source venv/bin/activate
```
### 4. Install Dependencies
Install the necessary Python libraries using pip:
```
pip install -r requirements.txt
```
### 5. Add Credentials
You must configure your API credentials within the app.py file. Open app.py and update the following placeholder variables:
```python
API_URL = "https://your-org-url.com/query/read"   # Replace with your org URL
LOGIN_ID = "your_login_id"                        # Replace with your login(email ID
PASSWORD = "your_password"                        # Replace with your password
ORG_ID = "your_org_id"                            # Replace with your organization ID
```
### 6. Run the Application
Start the Flask development server:
```python
python app.py
```
The application will start, and you can access it in your web browser at: http://127.0.0.1:5000/
