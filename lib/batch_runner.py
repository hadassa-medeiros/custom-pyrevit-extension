from room_validator import get_rvt_files, open_doc, validate_doc, save_doc
from file_utils import validate_doc

# batch_runner.py
def process_folder(folder_path):
    for rvt_file in get_rvt_files(folder_path):
        doc = open_doc(rvt_file)
        validate_doc(doc)
        save_doc(doc)

