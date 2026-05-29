from pathlib import Path


def get_latest_season_folder(dir: Path) -> Path:
    """Returns the path to the latest season folder in a given directory."""

    season_folders = list(dir.glob('season=*'))

    if not season_folders:
        raise FileNotFoundError(f'No season folders found in directory: {dir}')
    
    return max(season_folders)


def get_latest_path(dir: Path, file_type: str = None) -> Path:
    """
        Returns the latest path for the latest season in a given directory.

        Files should follow naming convention: dir/season=YYYY/YYYY-MM-DD where file name is date fetched.

        Params:
            dir(Path): Directory to be searched.
            file_type(str): What file type to search for - e.g. '.parquet' or '.*'. Leave as None to search for folders.

        Raises:
            FileNotFoundError: Raised if folder does not contain any files
    """

    latest_season_folder = get_latest_season_folder(dir)

    if file_type:
        paths = list(latest_season_folder.glob(f'*{file_type}'))
    else:
        paths = list(latest_season_folder.glob('*'))

    if not paths:
        raise FileNotFoundError(f'No files found in directory: {latest_season_folder}')
    
    return max(paths)


def get_latest_file_for_each_season(dir: Path, file_type: str) -> list[Path]:
    """
        Returns a list containing the latest file for each season.

        Files should follow naming convention: dir/season=YYYY/YYYY-MM-DD where file name is date fetched.

        Params:
            dir(Path): Directory containing historic files - e.g. data/raw/vaastav/fixtures.
            file_type(str): What file type to search for - e.g. '.parquet' or '.*'.

        Raises:
            FileNotFoundError: Raised if a season folder does not contain any files.
    """

    latest_files = []

    for season_folder in dir.glob('season=*'):
        file_list = list(season_folder.glob(f'*{file_type}'))

        if not file_list:
            raise FileNotFoundError(f'File not found in directory: {season_folder}')

        latest_file = max(file_list)
        latest_files.append(latest_file)

    return latest_files