# Jonathan's Automated Invoice Generation Script

This script is specifically designed for Jonathan Werle's strategic communication consulting work, enabling the efficient generation of PDF invoices from time-tracking data. While personalized for Jonathan, the script offers a template for automating similar tasks.

## Features

- **Automated PDF Invoice Generation**: Creates detailed invoices for each project from a CSV file.
- **Custom Footer Information**: Embeds Jonathan's contact details directly into each invoice for a professional touch.
- **Adaptable Template**: While tailored to Jonathan's needs, the script can be modified for other freelancers or small business owners.

## Usage

### Setting Up a Virtual Environment and Installing Dependencies

Ensure Python 3.x is installed on your system. 

Before running the script, it's a good practice to set up a Python virtual environment. This isolates your project dependencies, keeping your global site-packages directory clean and managing dependencies per project.

#### Creating a Virtual Environment

Navigate to your project directory in the terminal and run the following command to create a virtual environment named `venv`:

```sh
python3 -m venv venv
```

This command creates a `venv` directory in your project folder, containing the virtual environment.

#### Activating the Virtual Environment

Activate the virtual environment using the following command:

- On macOS and Linux:

```sh
source venv/bin/activate
```

- On Windows:

```cmd
.\venv\Scripts\activate
```

Your command line will indicate that you are now within the virtual environment by showing its name, like `(venv)`, before the prompt.

#### Installing Required Libraries

With the virtual environment activated, install the required libraries (`pandas` and `reportlab`) using `pip`:

```sh
pip install pandas reportlab
```

These commands install the `pandas` library for data manipulation and analysis, and `reportlab` for generating PDF files, within your virtual environment.

#### Deactivating the Virtual Environment

After running the script or installing any additional dependencies, you can deactivate the virtual environment by typing:

```sh
deactivate
```

This will return you to your global Python environment.

---

Including these steps ensures users unfamiliar with Python's virtual environments or project-specific dependencies can successfully set up and run your script. This addition complements your detailed README, making it accessible to a wider audience, including those who may not have extensive experience with Python development environments.

### Data Preparation

The script expects a CSV file containing time-tracking data with specific columns (start date, duration, task, client, and project name). Ensure your data matches this format.

### Script Customization

You might need to adjust the `draw_footer` function in the script to include your specific contact and business information.

### Invoice Generation

To generate invoices, run the script with the path to your CSV data file as an argument:

```sh
python3 script.py /path/to/your/timetracking_data.csv
```

## Automation with Automator (macOS)

For macOS users, the invoice generation process can be automated using Automator, bypassing the need to manually activate a Python virtual environment.

### Creating an Automator Quick Action

1. **Open Automator** and select "New Document".
2. Choose "Quick Action" as the document type.
3. Add a "Run Shell Script" action from the actions library.
4. Paste the following bash script, adjusting the path to your Python interpreter, likely the virtual environment we setup before:

```bash
#!/bin/bash

# First, run the Python script to read the CSV file and print its content
path/to/venv/bin/python3 -c '
import sys
import pandas as pd

... Rest of the script...

' "$@"
```

5. Save the Quick Action with a relevant name, like "Generate Invoice".

### Running Your Quick Action

You can access and run your Quick Action from the Finder by right-clicking on a file (e.g., your CSV data file) and navigating to the Quick Actions menu.