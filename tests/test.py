from pathlib import Path
from pytex_lib import write_to_latex


@write_to_latex
def get_output(answer: str):
    return answer

if __name__ == "__main__":

    # Path to latex doc
    file_path = Path(__file__).parent / 'test.tex'

    # Keyword
    keyword = "keyword in latex doc"

    # Answer to be written to the latex doc
    answer = "Response from python script."

    # Call the test function 
    get_output(
        answer=answer, 
        file_path=file_path, 
        keyword=keyword
    )
