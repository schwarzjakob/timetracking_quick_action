import sys
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

# Assuming the first argument is the CSV file path
csv_file = sys.argv[1]

try:
    df = pd.read_csv(csv_file)

    # Grouping by client and month
    grouped = df.groupby(["client", pd.to_datetime(df["start"]).dt.strftime("%m.%Y")])

    for group, data in grouped:
        client, month_year = group

        # Extract directory path from the CSV file path
        output_directory = os.path.dirname(csv_file)

        # Generate the PDF filename based on the client and current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        pdf_filename = os.path.join(
            output_directory, f"{current_date}_Stundennachweis_{client}_RNR.pdf"
        )

        def format_date(date_string):
            date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            return date_obj.strftime("%d.%m.%Y")

        def generate_pdf(dataframe, output_filename):
            c = canvas.Canvas(output_filename, pagesize=letter)

            # Title with current month and year
            title = "Stundennachweis " + month_year
            c.setFont("Helvetica-Bold", 12)
            c.drawString(30, letter[1] - 30, title)

            # Additional information
            auftraggeber = "Auftraggeber: " + client
            projekte = "\n".join(data["project"].unique())
            projektnamen = [
                projekt.split("_", 1)[1].replace("_", " ")
                for projekt in data["project"].unique()
            ]
            projektreferenzen = [
                projekt.split("_")[0] for projekt in data["project"].unique()
            ]

            c.setFont("Helvetica", 10)
            c.drawString(30, letter[1] - 50, auftraggeber)
            c.drawString(30, letter[1] - 70, "Projekt:")
            c.drawString(100, letter[1] - 70, "\n".join(projektnamen))
            c.drawString(30, letter[1] - 90, "Projektreferenz:")
            c.drawString(150, letter[1] - 90, "\n".join(projektreferenzen))

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
                datum = format_date(row["start"])  # Format Datum
                c.drawString(30, y_position, datum)  # Datum
                c.drawString(180, y_position, str(row["duration"]))  # Anzahl Stunden
                c.drawString(330, y_position, row["task"])  # Aufgabe

            c.save()

        generate_pdf(data, pdf_filename)

except Exception as e:
    print("Error:", e)
    sys.exit(1)
