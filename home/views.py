import os
import uuid
import base64
import pandas as pd
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ydata_profiling import ProfileReport
from dataset_profiler.settings import BASE_DIR

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

UPLOADS_DIR = f"{BASE_DIR}/uploads/"
ANALYSIS_DIR = f"{BASE_DIR}/analysis/"
FILE_NAME = "data.csv"
FILE_PATH = os.path.join(UPLOADS_DIR, FILE_NAME)
ANALYSED_FILE_PATH = os.path.join(ANALYSIS_DIR, "analysis.html")

# Ensure directories exist
for directory in [UPLOADS_DIR, ANALYSIS_DIR]:
    os.makedirs(directory, exist_ok=True)
    logger.debug(f"Directory created: {directory}")

def analyse_data(file_path):
    df = pd.read_csv(file_path)
    profile = ProfileReport(df, title="Profiling Report")
    html_file = profile.to_file(ANALYSED_FILE_PATH)
    logger.debug(f"Analysis file saved at: {ANALYSED_FILE_PATH}")

@csrf_exempt
def home(request):
    if request.method == 'POST':
        # Check if the request has a body
        if request.body:
            try:
                # Save the uploaded file with a unique name
                unique_filename = str(uuid.uuid4()) + "_" + FILE_NAME
                file_path = os.path.join(UPLOADS_DIR, unique_filename)
                with open(file_path, 'wb') as destination:
                    destination.write(request.body)

                logger.debug(f"Uploaded file saved at: {file_path}")

                # Analyze the uploaded file
                analyse_data(file_path)

                # Read the analyzed file, base64 encode its content, and return it in the response
                with open(ANALYSED_FILE_PATH, 'rb') as file:
                    file_content_base64 = base64.b64encode(file.read()).decode('utf-8')
                    return JsonResponse({'status': "success", 'file_content': file_content_base64})
            except FileNotFoundError:
                return JsonResponse({'status': "error", 'error': 'File not found'}, status=404)
            except Exception as e:
                return JsonResponse({'status': "error", 'error': str(e)}, status=500)
        else:
            return JsonResponse({'status': "error", 'error': 'No file uploaded'}, status=400)
    else:
        return JsonResponse({'status': "error", 'error': 'Only POST requests are allowed'}, status=405)
