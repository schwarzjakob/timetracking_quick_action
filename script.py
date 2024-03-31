import sys
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os


def format_date(date_string):
    date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    return date_obj.strftime("%d.%m.%Y")


def generate_pdf(
    dataframe,
    output_filename,
    invoice_month_year,
    client_name,
    project_name,
    project_reference,
):
    c = canvas.Canvas(output_filename, pagesize=letter)

    # Title with current month and year
    title = "Stundennachweis " + invoice_month_year
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, letter[1] - 30, title)

    c.setFont("Helvetica", 10)
    c.drawString(30, letter[1] - 50, "Auftraggeber: ")
    c.drawString(150, letter[1] - 50, client_name)
    c.drawString(30, letter[1] - 70, "project:")
    c.drawString(150, letter[1] - 70, project_name)
    c.drawString(30, letter[1] - 90, "projectreferenz:")
    c.drawString(150, letter[1] - 90, project_reference)

    # Table headers
    headers = ["Datum", "Anzahl Stunden", "Aufgabe"]
    y_position = (
        letter[1] - 130
    )  # Start position for printing rows after additional information
    for header in headers:
        c.drawString(30 + headers.index(header) * 150, y_position, header)

    # Table rows
    y_position -= 20
    for index, row in dataframe.iterrows():
        y_position -= 20
        date = format_date(row["start"])  # Format Datum
        c.drawString(30, y_position, date)  # Datum
        c.drawString(180, y_position, str(row["duration"]))  # Anzahl Stunden
        c.drawString(330, y_position, row["task"])  # Aufgabe

    c.save()


# Assuming the first argument is the CSV file path
csv_file = sys.argv[1]

try:
    timetracking_df = pd.read_csv(csv_file)

    # Grouping by client and project
    grouped_timetracking_df = timetracking_df.groupby(["client", "project"])

    # Extract the month and year from the first row of the CSV file
    invoice_month_year = pd.to_datetime(timetracking_df["start"].iloc[0]).strftime(
        "%m.%Y"
    )

    for (client_name, project), client_project_df in grouped_timetracking_df:
        # Additional project information
        project_name = project.split("_", 1)[1].replace("_", " ")
        project_reference = project.split("_")[0]

        # Extract directory path from the CSV file path and define output directory
        current_directory = os.path.dirname(csv_file)
        output_directory = os.path.join(current_directory, "invoices")

        # Create the output directory if it does not exist
        os.makedirs(output_directory, exist_ok=True)

        # Generate the PDF filename based on the client and current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        client_project_pdf_filename = os.path.join(
            output_directory, f"{current_date}_Stundennachweis_{project_name}_RNR.pdf"
        )

        generate_pdf(
            client_project_df,
            client_project_pdf_filename,
            invoice_month_year,
            client_name,
            project_name,
            project_reference,
        )

except Exception as e:
    print("Error:", e)
    sys.exit(1)
