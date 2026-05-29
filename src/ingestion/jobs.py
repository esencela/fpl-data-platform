from ingestion.extract import (
    fpl_extract,
    vaastav_extract,
    understat_extract
)

from ingestion.load import (
    fpl_load,
    vaastav_load,
    understat_load
)

JOBS = {
    'fpl_extract': fpl_extract.run_fpl_extract,
    'vaastav_extract': vaastav_extract.run_vaastav_extract,
    'understat_extract': understat_extract.run_understat_extract,
    'fpl_load': fpl_load.run_fpl_load,
    'vaastav_load': vaastav_load.run_vaastav_load,
    'understat_load': understat_load.run_understat_load
}