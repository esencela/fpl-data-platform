from src.ingestion.extract import (
    fpl_extract,
    vaastav_extract,
    understat_extract
)

from src.ingestion.load import (
    fpl_load,
    vaastav_load,
    understat_load
)

JOBS = {
    'fpl_extract': fpl_extract,
    'vaastav_extract': vaastav_extract,
    'understat_extract': understat_extract,
    'fpl_load': fpl_load,
    'vaastav_load': vaastav_load,
    'understat_load': understat_load
}