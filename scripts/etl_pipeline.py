from clean import clean
from ingest import ingest
from optimize import create_indexes
from quality_check import quality_check
from versioning import archive_version
from metadata import update_metadata

print("Starting ETL pipeline")

# extract the raw data and transform it (clean + fix types)
clean()

# load the clean data into the warehouse
ingest()

# re-create indexes (table replace during load drops them)
create_indexes()

# inspect the loaded data and log the results
quality_check()

# archive a dated snapshot of the cleaned dataset
archive_version()

# refresh the metadata table (structure, sources, lineage)
update_metadata()

print("ETL pipeline finished")