import json
import re
from pathlib import Path
from datetime import date, datetime

import pandas as pd


def format_val(value, col_name=""):
    """Convert spreadsheet values into clean, JSON-safe strings."""
    if pd.isna(value):
        return ""

    # Handle dates before converting values to strings.
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.strftime("%Y-%m-%d")

    column = str(col_name).strip().lower()

    # Convert numeric values without unnecessary trailing zeroes.
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if any(word in column for word in ("profit", "allocation")) or "%" in column:
            return f"{value * 100:.1f}%"

        return f"{value:,.2f}".rstrip("0").rstrip(".")

    return str(value).strip()


def extract_data_to_json(file_path: str, ext: str | None = None) -> dict:
    """
    Read every sheet from an Excel workbook, or one CSV file.

    Returns:
        {
            "Sheet name": [
                {"Column A": "value", "Column B": "value"}
            ]
        }
    """
    path = Path(file_path)
    extension = (ext or path.suffix).lower()

    if extension == ".csv":
        sheets = {"CSV Data": pd.read_csv(path)}
    elif extension in {".xlsx", ".xls", ".xlsm"}:
        sheets = pd.read_excel(path, sheet_name=None)
    else:
        raise ValueError(
            f"Unsupported file extension: {extension}. "
            "Supported formats: .csv, .xlsx, .xls, .xlsm"
        )

    json_data = {}

    for sheet_name, dataframe in sheets.items():
        # Remove completely empty rows, but keep the sheet even if it has no data.
        dataframe = dataframe.dropna(how="all")

        records = []
        for record in dataframe.to_dict(orient="records"):
            clean_record = {}

            for column, value in record.items():
                formatted_value = format_val(value, column)
                if formatted_value != "":
                    clean_record[str(column).strip()] = formatted_value

            # Ignore rows where every cell is blank.
            if clean_record:
                records.append(clean_record)

        json_data[str(sheet_name)] = records

    return json_data


def build_whatsapp_catalogs(json_data: dict) -> list:
    categories = []

    for sheet_name, records in json_data.items():
        category_rows = []

        for row_number, record in enumerate(records, start=1):
            values = {
                key: value
                for key, value in record.items()
                if value is not None and str(value).strip() != ""
            }

            if not values:
                continue

            columns = list(values.keys())

            # First column = title (no truncation)
            title = str(values[columns[0]]).strip()

            # Remaining columns = complete description
            description_parts = [
                f"{column}: {values[column]}"
                for column in columns[1:]
            ]

            description = " | ".join(description_parts)

            category_rows.append({
                "id": f"row_{len(category_rows) + 1}",
                "title": title,
                "description": description or "No additional data"
            })

        # One category per sheet
        categories.append({
            "title": str(sheet_name).strip(),
            "rows": category_rows
        })

    return categories


def parse_spreadsheet_to_catalogs(file_path: str, ext: str | None = None) -> list:
    """Main entry point: read a spreadsheet and return sheet-wise categories."""
    json_data = extract_data_to_json(file_path, ext)
    return build_whatsapp_catalogs(json_data)
