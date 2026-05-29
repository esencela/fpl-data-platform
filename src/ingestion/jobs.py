from ingestion.extract.fpl_extract import run_fpl_extract
from ingestion.extract.vaastav_extract import run_vaastav_extract
from ingestion.extract.understat_extract import run_understat_extract

from ingestion.load.fpl_load import run_fpl_load
from ingestion.load.vaastav_load import run_vaastav_load
from ingestion.load.understat_load import run_understat_load

JOBS = {
    'fpl-extract': run_fpl_extract,
    'vaastav-extract': run_vaastav_extract,
    'understat-extract': run_understat_extract,
    'fpl-load': run_fpl_load,
    'vaastav-load': run_vaastav_load,
    'understat-load': run_understat_load
}