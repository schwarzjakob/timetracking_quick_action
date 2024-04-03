import sys
import pandas as pd
from datetime import datetime
import os
import re

# Import necessary modules from reportlab
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register the font (only needs to be done once)
font_path_bold = sys.argv[2] + "/font-bold.ttf"
font_name_bold = "font-bold"

font_path_medium = sys.argv[2] + "/font-medium.ttf"
font_name_medium = "font-medium"

pdfmetrics.registerFont(TTFont(font_name_bold, font_path_bold))
pdfmetrics.registerFont(TTFont(font_name_medium, font_path_medium))

# Define custom styles
custom_styles = {
    "title": ParagraphStyle(
        name="Title",
        fontSize=18,
        leading=22,
        alignment=TA_LEFT,
        spaceAfter=20,
        fontName=font_name_bold,  # Ensure title is bold
    ),
    "body": ParagraphStyle(
        name="Body",
        fontSize=12,
        leading=14,
        spaceAfter=6,
        fontName=font_name_medium,  # Normal text, not bold
    ),
    "table_heading": ParagraphStyle(
        name="TableHeading",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        textColor=black,
        fontName=font_name_bold,  # Ensure table headings are bold
        spaceAfter=6,
    ),
    "table_body": ParagraphStyle(
        name="TableBody",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        textColor=black,
        fontName=font_name_medium,  # Normal text, not bold for table body
    ),
}


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


def add_pdf_background(pdf_path, background_pdf_path):
    """
    Adds a PDF background to the input PDF file.

    Args:
    - input_pdf_path: Path to the generated PDF invoice.
    - background_pdf_path: Path to the PDF file to use as background.
    - output_pdf_path: Path to save the final PDF file with background.
    """
    # Load the background PDF
    background_reader = PdfReader(background_pdf_path)
    background_page = background_reader.pages[0]

    # Load the generated invoice PDF
    input_reader = PdfReader(pdf_path)
    input_page = input_reader.pages[0]

    # Create a writer for the output PDF
    writer = PdfWriter()

    # Merge the invoice content onto the background page
    background_page.merge_page(input_page)

    # Add the merged page to the writer
    writer.add_page(background_page)

    # Write the output PDF file
    with open(pdf_path, "wb") as f_out:
        writer.write(f_out)


def generate_project_invoice_as_pdf(
    dataframe,
    output_directory_and_filename,
    invoice_month_year,
    client_name,
    project_name,
    project_reference,
):
    """ " Generates a PDF invoice for a project based on the provided DataFrame."""

    # Define the page size and margins
    page_width, page_height = A4
    top_bottom_margin = 72  # 2.54 cm in points
    left_right_margin = 54  # 1.91 cm in points
    print(page_width, page_height, top_bottom_margin, left_right_margin)

    # Create a document with margins
    doc = SimpleDocTemplate(
        output_directory_and_filename,
        pagesize=A4,
        rightMargin=left_right_margin,
        leftMargin=left_right_margin,
        topMargin=top_bottom_margin,
        bottomMargin=top_bottom_margin,
    )
    story = []
    styles = getSampleStyleSheet()

    # Add invoice title
    story.append(
        Paragraph("Stundennachweis " + invoice_month_year, custom_styles["title"])
    )

    # Add client and project info
    # Prepare data for the table
    client_project_data = [
        ["Auftraggeber: ", client_name],
        ["Projekt: ", project_name],
        ["Projektreferenz: ", project_reference],
    ]

    # Create the table
    client_project_table = Table(
        client_project_data, colWidths=[100, page_width - 2 * left_right_margin - 100]
    )
    client_project_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), font_name_medium),
                ("FONTNAME", (0, 1), (-1, -1), font_name_medium),
            ]
        )
    )

    story.append(client_project_table)

    # Space before the table
    story.append(Spacer(1, 20))

    # Prepare data for the table including header
    data = [["Datum", "Anzahl Stunden", "Aufgabe"]] + [
        [format_date(row["start"]), row["duration"], row["task"]]
        for _, row in dataframe.iterrows()
    ]
    total_duration = dataframe["duration"].sum()
    data.append(["Summe ", total_duration, ""])

    # Calculate the width of the page minus the margins and the column widths
    content_width = page_width - 2 * left_right_margin
    col1_width = 100
    col2_width = 100
    col3_width = content_width - col1_width - col2_width
    print(content_width, col1_width, col2_width, col3_width)

    # Create the table
    column_widths = [col1_width, col2_width, col3_width]
    data_table = Table(data, colWidths=column_widths)
    data_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                # Apply custom styles to table headings and body
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    custom_styles["table_heading"].textColor,
                ),
                ("FONTNAME", (0, 0), (-1, 0), custom_styles["table_heading"].fontName),
                ("TEXTCOLOR", (0, 1), (-1, -1), custom_styles["table_body"].textColor),
                ("FONTNAME", (0, 1), (-1, -1), custom_styles["table_body"].fontName),
                (
                    "FONTNAME",
                    (0, -1),
                    (-1, -1),
                    custom_styles["table_heading"].fontName,
                ),  # Make last row bold
            ]
        )
    )

    story.append(data_table)
    doc.build(story)


if __name__ == "__main__":
    # Assuming the first argument is the CSV file path
    csv_file = sys.argv[1]
    pdf_background = sys.argv[2] + "/background.pdf"

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
        add_pdf_background(output_directory_and_filename, pdf_background)

    print("PDF invoices successfully generated.")
