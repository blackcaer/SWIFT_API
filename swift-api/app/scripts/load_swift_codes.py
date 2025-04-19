import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session
import argparse
import sys

# Fix imports add project to PYTHONPATH
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
from app.models import SwiftCode

load_dotenv()
DEFAULT_EXCEL_FILE_PATH = "app/data/Interns_2025_SWIFT_CODES.xlsx"
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"


def validate_columns(df: pd.DataFrame):
    """Checks for required columns in the Excel file"""
    required_columns = {
        "COUNTRY ISO2 CODE",
        "SWIFT CODE",
        "NAME",
        "ADDRESS",
        "TOWN NAME",
        "COUNTRY NAME",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def load_swift_data(file_path: Path):
    """Loads data from an Excel file and inserts it into the database"""
    engine = create_engine(DATABASE_URL)

    try:
        df = pd.read_excel(file_path)
        validate_columns(df)
        print(f"Found {len(df)} records in the file")

        records = []
        for idx, row in df.iterrows():
            try:
                records.append(
                    SwiftCode(
                        swiftCode=row["SWIFT CODE"],
                        bankName=row["NAME"],
                        address=row["ADDRESS"],
                        countryISO2=row["COUNTRY ISO2 CODE"].upper(),
                        countryName=row["COUNTRY NAME"],
                        isHeadquarter=row["SWIFT CODE"].endswith("XXX"),
                    )
                )
            except Exception as e:
                print(
                    f"Error in row {idx + 2}: {str(e)}", file=sys.stderr
                )  # Excel rows are 1-indexed + header row
                continue

        with Session(engine) as session:
            session.add_all(records)
            session.commit()
            print(f"\nSuccessfully loaded {len(records)}/{len(df)} SWIFT codes into the database")
            if len(records) != len(df):
                print(f"Skipped {len(df) - len(records)} invalid records", file=sys.stderr)

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    argparser = argparse.ArgumentParser(description="Load SWIFT codes from Excel to database")
    argparser.add_argument(
        "-f",
        "--file",
        type=str,
        default=DEFAULT_EXCEL_FILE_PATH,
        help=f"Path to Excel file (default: ${DEFAULT_EXCEL_FILE_PATH})",
    )

    args = argparser.parse_args()
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: Input file not found at {file_path}", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print(f"1. Place your file in {file_path.parent}", file=sys.stderr)
        print("2. Provide full path using --file argument", file=sys.stderr)
        sys.exit(1)

    load_swift_data(file_path)


if __name__ == "__main__":
    main()
