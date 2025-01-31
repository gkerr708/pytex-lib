from pathlib import Path
from pytex_lib.core import write_to_latex


if __name__ == "__main__":
    file_path = Path(__file__).parent / 'test.tex'

    @write_to_latex
    def get_output():
        return 'Hello, World!'

    keyword = 'keyword'
    get_output(file_path = file_path, keyword = 'keyword')
    print('Done!')

