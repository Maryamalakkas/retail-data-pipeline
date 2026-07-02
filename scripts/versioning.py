import shutil
import os
from datetime import datetime


def archive_version():
    # Name each snapshot by date and time so versions never collide
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    archive_path = f"data/archive/online_retail_clean_{timestamp}.csv"

    # Make sure the archive folder exists
    os.makedirs("data/archive", exist_ok=True)

    # Copy the current processed file into the archive
    shutil.copy("data/processed/online_retail_clean.csv", archive_path)
    print("Version archived:", archive_path)


if __name__ == "__main__":
    archive_version()