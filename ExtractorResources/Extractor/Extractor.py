from datetime import datetime
import logging
import os
import tempfile

from ExtractorResources.Cases.COJ.extractor_COJ import *

class Extractor():
    def __init__(self,req):
        logging.info("Intializing Extractor")
        self.req = req
        # self.file_type = self.req.files['file_type']
        self.file_type = "COJ"
        
        if self.file_type.upper() == "COJ":
            logging.info("{} extractor requested".format(self.file_type))
            self.extraction = ExtractorCOJ()
            pass
        else:
            raise NameError("{} not recognised".format(self.file_type))
                       
    def print_test(self):
        return f"{self.file_type} test "+ str(datetime.now())
    
    # Create PDF and JSON template           
    def create_files(self):
        # Save the file to a temporary location
        logging.info("Getting file from request")
        file = self.req.files['file']
                              
        # Create temp file                              
        fd, path = tempfile.mkstemp()
                
        # Write file content
        with os.fdopen(fd , 'wb') as tmp:
            tmp.write(file.stream.read())
       
        #Read file and template       
        logging.warning(f"Reading {path}")
        self.raw_extracted_text, self.empty_JSON_Template = self.extraction.readpdf_and_json(path)
            
        logging.info(f"Deleting local file: {path}")
        os.remove(path)
        
        return self.raw_extracted_text, self.empty_JSON_Template
    
    # Fill JSON template with PDF data
    def filler(self):
        logging.info("Inserting file data")
        self.JSON_Template =  self.extraction.regex_into_template()
        return self.JSON_Template
        

    