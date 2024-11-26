# ClickUp Task Comments Exporter

This project retrieves comments from tasks in ClickUp using its API and exports the data to a CSV file for analysis or record-keeping.

## Features

- Fetches comments for a list of tasks from ClickUp.
- Extracts detailed information for each comment, including text, user info, attachments, reactions, and more.
- Supports configuration via environment variables for flexible usage.
- Outputs the extracted data to a CSV file with a timestamp.

---

## Requirements

- Python 3.8 or higher
- A valid ClickUp API Key
- Libraries: `requests`, `pandas`, `python-dotenv`, `openpyxl`

---

## Installation

1. Clone this repository:

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the root directory and add the following variables:

   ```env
   API_KEY=your_clickup_api_key
   COLUMN_ID_NAME=task_id  # Optional, default is 'task_id'
   FILE_NAME=tasks.xlsx    # Optional, default is 'tasks.xlsx'
   SLEEP_TIME=0.2          # Optional, default is 0.2 seconds
   ```

4. Prepare an Excel file (`tasks.xlsx` by default) with a column containing task IDs to process. Ensure the column matches the name specified in `COLUMN_ID_NAME` or the default (`task_id`).

---

## Usage

Run the script with:

```bash
python main.py
```
