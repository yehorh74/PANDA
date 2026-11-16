import sys
import traceback
import os

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        
    log_path = os.path.join(app_dir, "crash.log")
    
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("=== RAPORT KRAXU PANDA ===\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
        
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_handler