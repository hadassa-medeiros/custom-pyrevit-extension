
import clr
clr.AddReference("System")
from System import ArgumentException

def get_rvt_files(folder_path):
    """
    Recursively retrieves all Revit (.rvt) files from the specified folder.
    Args:
        folder_path (str or Path): The path to the folder to search for .rvt files.
    Returns:
        list of Path: A list of pathlib.Path objects representing the found .rvt files.
    """
    import os
    from pathlib import Path

    rvt_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.rvt'):
                rvt_files.append(Path(root) / file)
    return rvt_files

def open_doc(rvt_file):
    """
    Opens a Revit project file and returns the corresponding Document object.

    Args:
        rvt_file (str or Path): The path to the Revit (.rvt) file to open.

    Returns:
        Autodesk.Revit.DB.Document: The opened Revit document object.

    Raises:
        Autodesk.Revit.Exceptions.ArgumentException: If the file path is invalid or the file cannot be opened.
    """
    from Autodesk.Revit.DB import DocumentManager
    try:
        doc = DocumentManager.Instance.CurrentUIApplication.Application.OpenDocumentFile(str(rvt_file))
        return doc
    except ArgumentException as ae:
        raise ArgumentException("Failed to open file {}: {}".format(rvt_file, ae))
    except Exception as e:
        raise Exception("Unexpected error while opening file {}: {}".format(rvt_file, e))

def save_doc(doc):
    """
    Saves the given Revit document within a transaction.

    Args:
        doc (Autodesk.Revit.DB.Document): The Revit document to be saved.

    Raises:
        Autodesk.Revit.Exceptions.InvalidOperationException: If the document cannot be saved.

    Side Effects:
        Commits a transaction to save the document and prints a confirmation message.
    """
    from Autodesk.Revit.DB import Transaction
    t = Transaction(doc, "Save Document")
    t.Start()
    doc.Save()
    t.Commit()
    print(f"Document {doc.Title} saved successfully.")
