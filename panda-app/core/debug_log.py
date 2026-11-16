import sys
import traceback
import os

def global_exception_handler(exc_type, exc_value, exc_traceback):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    report_path = os.path.join(desktop_path, "panda_crash.txt")
    
    error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("--- ERROR RAPORT ---\n")
            f.write(error_details)
    except Exception:
        pass
    
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
