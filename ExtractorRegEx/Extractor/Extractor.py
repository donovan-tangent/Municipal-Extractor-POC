from datetime import datetime
import logging
import os
import tempfile
import json
import PyPDF2
import re

#__________________________________________________________________________________________________________________________________________________________

def RE_Extractor(text, pattern):
        # text = text.replace("\\","\\\\")
        result = re.search(pattern, text)
        if result:
            text_found = result.group(0)
            # print(text_found)
            return text_found
        else:
            print("No match")
            return ""
        
# Function to extract a pattern and return the match or returns no match if none found
def Trim_Extractor(text, pattern):
    text = text.replace("\\","\\\\")
    result = re.search(pattern, text)
    if result:
        text_found = result.group(0)
        # print(text_found)
        return text.replace(text_found,"").strip()
    else:
        print("No match")
        return text
    
#__________________________________________________________________________________________________________________________________________________________
# CANT IMPORT?
# from ExtractorRegEx.Cases.COJ.COJ_Extractor import *
class COJ_Extractor:
    
    def __init__(self):
        logging.info("Intializing COJ Extracter")
         
            
    # Read PDF file and JSON template      
    def ReadPDFAndJSON(self, file):
        # Open the PDF file in read binary mode using the with statement
        self.file = file
        self.raw_extracted_text = ""
        
        # Read PDF
        with open(self.file, "rb") as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Get the number of pages in the PDF file
            num_pages = len(pdf_reader.pages)

            # Loop through each page and extract the text
            
            for page in range(num_pages):
                page_obj = pdf_reader.pages[page]
                text = page_obj.extract_text()
                self.raw_extracted_text = self.raw_extracted_text + "\n" + text

        # Open the JSON file in read mode
        logging.info("Reading COJ Template")
        with open(r"ExtractorRegEx\Cases\COJ\COJ_Template.json", "r") as json_file:

            # Load the contents of the file into a dictionary object
            self.empty_COJ_Template = json.load(json_file)
                                
        return self.raw_extracted_text, self.empty_COJ_Template
    
    # Insert RegEx info into JSON template
    def RegExIntoTemplate(self):
        
        self.COJ_Template = self.empty_COJ_Template
        
        # Remove Headers up to Date
        self.extracted_text = Trim_Extractor(self.raw_extracted_text,"You can contact us in the following ways(.*\n)*2125")
        logging.warn("Trim header")
        # Remove Footer from Where can a payment be made?
        self.extracted_text = Trim_Extractor(self.raw_extracted_text,"Where can a payment be made(\s|\S)*")
        logging.warn("Trim footer")
        # Get Date 
        InvoiceDate = RE_Extractor(self.extracted_text,"Date\n\d{4}/\d{2}/\d{2}")
        self.COJ_Template["InvoiceDate"] = InvoiceDate.replace("Date","").strip()
        self.extracted_text = Trim_Extractor(self.extracted_text,"Date\n\d{4}/\d{2}/\d{2}")

        # # Remove Statement info 
        # extracted_text = Trim_Extractor(extracted_text,"(.|\n)*(?=Invoice Number)")
        # # print(extracted_text)

        # # Get InvoiceNumber and Remove unwanted text up to Total Due
        # InvoiceNumeber = RE_Extractor(extracted_text,"(?!Invoice Number:\s*)(\d+)")
        # COJ_Template["InvoiceDate"] = InvoiceNumeber
        # extracted_text = Trim_Extractor(extracted_text,"(\s|\S)*(?=Current Charges \(Excl. VAT\))")

        # # Get Current Charges and remove the text
        # CurrentCharges_Excl = RE_Extractor(extracted_text,"(?!Current Charges \(Excl. VAT\))\n.*").strip()
        # extracted_text = Trim_Extractor(extracted_text,"Current Charges \(Excl. VAT\)\n.*")
        # CurrentCharges_VAT = RE_Extractor(extracted_text,"(?!VAT @ 15%)\n.*").strip()
        # extracted_text = Trim_Extractor(extracted_text,"VAT @ 15%\n.*")
        # CurrentCharges = str(float(CurrentCharges_VAT)+float(CurrentCharges_Excl))
        # COJ_Template["CurrentCharges"] = CurrentCharges

        # # Get Due Date and remove unwanted text
        # DueDate = RE_Extractor(extracted_text,"(Due Date)\n.*\n\d{4}/\d{2}/\d{2}").replace(RE_Extractor(extracted_text,"(Due Date)\n.*"),"").strip()
        # extracted_text = Trim_Extractor(extracted_text,"(\s|\S)*(?=Account Number)")
        # COJ_Template["DueDate"] = DueDate

        # # Get Account Number and remove text
        # AccountNumber = RE_Extractor(extracted_text,"(Account Number:).*").replace(RE_Extractor(extracted_text,"(Account Number:)"),"").strip()
        # extracted_text = Trim_Extractor(extracted_text,"(Account Number:).*")
        # COJ_Template["AccountNumber"] = AccountNumber


        # # Check which services are on the invoice
        # # PIKITUP
        # if "pikitup" in extracted_text.lower():
        #     COJ_Template["isRefuse"] = True

        # # print(COJ_Template)
        return self.extracted_text, self.COJ_Template
#__________________________________________________________________________________________________________________________________________________________

class Extractor():
    def __init__(self,req):
        logging.info("Intializing Extractor")
        self.req = req
        # self.file_type = self.req.files['file_type']
        self.file_type = "COJ"
        
        if self.file_type.upper() == "COJ":
            logging.info("{} extractor requested".format(self.file_type))
            self.extraction = COJ_Extractor()
            pass
        else:
            raise NameError("{} not recognised".format(self.file_type))
                       
    def printTest(self):
        return f"{self.file_type} test "+ str(datetime.now())
    
    # Create PDF and JSON template           
    def createFiles(self):
        # Save the file to a temporary location
        logging.info("Getting file from request")
        file = self.req.files['file']
                              
        # Create temp file                              
        fd, path = tempfile.mkstemp()
        logging.warn(f"File path: {path}")
        
        # Write file content
        with os.fdopen(fd , 'wb') as tmp:
            tmp.write(file.stream.read())
        
        
        #Read file and template       
        logging.warn(f"Reading {path}")
        self.raw_extracted_text, self.empty_JSON_Template = self.extraction.ReadPDFAndJSON(path)
            
        logging.info(f"Deleting local file: {path}")
        os.remove(path)
        
        return self.raw_extracted_text, self.empty_JSON_Template
    
    # Fill JSON template with PDF data
    def filler(self):
        logging.info("Inserting file data")
        self.extracted_text, self.JSON_Template = self.extraction.RegExIntoTemplate()
        return self.extracted_text, self.JSON_Template
        

    # Function to extract a pattern and return the match or returns no match if none found


TEST = COJ_Extractor()
a,b =TEST.ReadPDFAndJSON(r"C:\Users\DonovanE\Desktop\CTM Strijdompark Erf 377 330047840 (Waste).pdf")

print(a)


