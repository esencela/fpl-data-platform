from ingestion.extract import fpl_extract

def test_sanity():
    assert hasattr(fpl_extract, "run_fpl_extract")