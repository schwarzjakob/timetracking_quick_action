import sys
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
import os
import re


def prepare_project_data(timetracking_df):
    """
    Prepares data by grouping the DataFrame by client and project,
    and extracts necessary details for invoice generation.
    """
    invoice_month_year = pd.to_datetime(timetracking_df["start"].iloc[0]).strftime(
        "%m.%Y"
    )
    grouped_timetracking_df = timetracking_df.groupby(["client", "project"])

    prepared_data = []
    for (client_name, project), client_project_df in grouped_timetracking_df:
        project_name = project.split("_", 1)[1].replace("_", " ")
        project_reference = project.split("_")[0]
        prepared_data.append(
            (client_name, project_name, project_reference, client_project_df)
        )

    return invoice_month_year, prepared_data


def extract_project_details(project):
    """Extracts and returns project name and reference from a combined project string."""
    project_name = project.split("_", 1)[1].replace("_", " ")
    project_reference = project.split("_")[0]
    return project_name, project_reference


def sanitize_filename(project_name):
    """Removes or replaces characters in names that are invalid for filenames."""
    return re.sub(r"[<>:\"/\\|?*]", "_", project_name)


def construct_pdf_filename(output_directory, project_name):
    """Constructs a sanitized PDF filename based on the project name."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    project_name = sanitize_filename(project_name)  # Sanitize project name for filename
    return os.path.join(
        output_directory, f"{current_date}_Stundennachweis_{project_name}_RNR.pdf"
    )


def format_date(date_string):
    """Formats the date string from the DataFrame to a German date format."""
    date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    return date_obj.strftime("%d.%m.%Y")


def generate_project_invoice_as_pdf(
    dataframe,
    output_directory_and_filename,
    invoice_month_year,
    client_name,
    project_name,
    project_reference,
):
    """" Generates a PDF invoice for a project based on the provided DataFrame."""
    doc = SimpleDocTemplate(output_directory_and_filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Add invoice title
    story.append(Paragraph("Stundennachweis " + invoice_month_year, styles["Title"]))
    
    # Add client and project info
    story.append(Spacer(1, 12))  # Add some space
    story.append(Paragraph("Auftraggeber: " + client_name, styles["Normal"]))
    story.append(Paragraph("Projekt: " + project_name, styles["Normal"]))
    story.append(Paragraph("Projektreferenz: " + project_reference, styles["Normal"]))
    
    story.append(Spacer(1, 20))  # Space before the table
    
    # Prepare data for the table including header
    data = [["Datum", "Anzahl Stunden", "Aufgabe"]] + [
        [format_date(row["start"]), row["duration"], row["task"]] for _, row in dataframe.iterrows()
    ]
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 12),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))
    
    story.append(table)
    
    doc.build(story)



if __name__ == "__main__":
    # Assuming the first argument is the CSV file path
    csv_file = sys.argv[1]

    # Extract directory path from the CSV file path and define output directory
    current_directory = os.path.dirname(csv_file)
    output_directory = os.path.join(current_directory, "invoices")

    # Create the output directory if it does not exist
    os.makedirs(output_directory, exist_ok=True)

    timetracking_df = pd.read_csv(csv_file)
    invoice_month_year, prepared_data = prepare_project_data(timetracking_df)

    for (
        client_name,
        project_name,
        project_reference,
        client_project_df,
    ) in prepared_data:
        output_directory_and_filename = construct_pdf_filename(
            output_directory, project_name
        )
        generate_project_invoice_as_pdf(
            client_project_df,
            output_directory_and_filename,
            invoice_month_year,
            client_name,
            project_name,
            project_reference,
        )

    print("PDF invoices successfully generated.")
