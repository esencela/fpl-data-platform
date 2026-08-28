import sys
import logging
from ingestion.jobs import JOBS

logging.basicConfig(
    level=logging.INFO
)


def main():
    if len(sys.argv) < 2:
        print("Please provide a job name to run. Available jobs:")
        for job_name in JOBS.keys():
            print(f" - {job_name}")
        sys.exit(1)

    job_name = sys.argv[1]
    job_args = sys.argv[2:]  # Additional arguments for the job

    if job_name not in JOBS:
        print(f"Invalid job name: {job_name}. Available jobs:")
        for job_name in JOBS.keys():
            print(f" - {job_name}")
        sys.exit(1)

    JOBS[job_name](*job_args)


if __name__ == "__main__":
    main()