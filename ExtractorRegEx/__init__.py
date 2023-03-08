import logging
import os
import tempfile
import json
import datetime

import azure.functions as func

from ExtractorRegEx.Extractor.Extractor import *


def main(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('Extractor HTTP request called')
    
    try:
        # Return a JSON response with the URL of the saved file
        FileEx = Extractor(req)
        # test = FileEx.printTest()
        raw_extracted_text, empty_JSON_template = FileEx.createFiles()
        extracted_text, JSON_template = FileEx.filler()
        response = {
            "message": f"{FileEx.file_type} file extraction was successfull",
            "extracted_text": extracted_text,
            "JSON_template": JSON_template
            }
        return func.HttpResponse(
            body=json.dumps(response),
            mimetype="application/json"
        )
    except Exception as e:
        # Handle any errors that occur during the upload process
        response = {
            "message": f"An error occurred during the extraction process: {str(e)}"
        }



        return func.HttpResponse(
            body=json.dumps(response),
            status_code=500,
            mimetype="application/json"
        )