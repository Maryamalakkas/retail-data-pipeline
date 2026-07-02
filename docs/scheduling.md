# Scheduling the ETL Pipeline

The whole pipeline is one command, so a scheduler just needs
to run that command on a clock. On macOS/Linux the built-in
scheduler is cron.

To run the pipeline every day at 02:00, this line is added to cron:

0 2 * * * cd /path/to/Nesma_2 && venv/bin/python scripts/etl_pipeline.py >> docs/pipeline_runs.log 2>&1

What it means:
- "0 2 * * *" = minute 0, hour 2, every day = daily at 02:00
- cd into the project so all file paths work
- run the pipeline with the project's own Python (the venv)
- ">> docs/pipeline_runs.log 2>&1" = append everything the pipeline
  prints (receipts, quality report, and any errors) into a log file,
  so every run leaves a record even with no human watching

In production this would run on a server via Airflow or a cloud
scheduler, which adds retries and failure alerts. Cron shown here
for simplicity.