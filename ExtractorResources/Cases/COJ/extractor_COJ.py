import PyPDF2
import json
import logging
import re

#__________________________________________________________________________________________________________________________________________________________
# CANT IMPORT?
# from ExtractorResources.RegExFuncs import re_extractor
def re_extractor(text, pattern):
        # text = text.replace("\\","\\\\")
        result = re.search(pattern, text)
        if result:
            text_found = result.group(0)
            # print(text_found)
            return text_found.strip()
        else:
            print("No match")
            return ""
        
# Function to extract a pattern and return the match or returns no match if none found
def trim_extractor(text, pattern):
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


class ExtractorCOJ:
    
    def __init__(self):
        logging.info("Intializing COJ Extracter")
         
            
    # Read PDF file and JSON template      
    def readpdf_and_json(self, file):
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
        with open(r"ExtractorResources\Cases\COJ\COJ_Template.json", "r") as json_file:

            # Load the contents of the file into a dictionary object
            self.empty_coj_template = json.load(json_file)
                                
        return self.raw_extracted_text, self.empty_coj_template
    
    # Insert RegEx info into JSON template
    def regex_into_template(self):
        
        self.coj_template = self.empty_coj_template
        
        # Remove Headers up to Date
        # NB only use self.raw_extracted text for the line below, thereafter self.extracted_text
        self.extracted_text = trim_extractor(self.raw_extracted_text,"You can contact us in the following ways(.*\n)*2125")
        logging.info("Trim header")
        # Remove Footer from Where can a payment be made?
        self.extracted_text = trim_extractor(self.extracted_text,"Where can a payment be made(\s|\S)*")
        logging.info("Trim footer")
        
        # Get Date and remove unwanted text up to Current Charges
        InvoiceDate = re_extractor(self.extracted_text,"(?!Date) \d{4}/\d{2}/\d{2}")
        self.coj_template["InvoiceDate"] = InvoiceDate
        # Remove Statement info 
        self.extracted_text = trim_extractor(self.extracted_text,"(\s|\S)*(?=Current Charges \(Excl. VAT\))")

        # Get Current Charges, Due Date and remove text up to Account Number
        current_charges_excl = trim_extractor(re_extractor(self.extracted_text,"(Current Charges \(Excl. VAT\)).*"),"(Current Charges \(Excl. VAT\))").replace(",","")
        current_charges_vat = re_extractor(re_extractor(self.extracted_text,"VAT.*\@.*\d*"),"\d*\.\d*").replace(",","")
        current_charges = str(float(current_charges_vat)+float(current_charges_excl))
        self.coj_template["CurrentCharges"] = current_charges
        # Get Due Date
        DueDate = re_extractor(re_extractor(self.extracted_text,"Due Date \d{4}/\d{2}/\d{2}"),"\d{4}/\d{2}/\d{2}")
        # Remove unwanted info 
        self.extracted_text = trim_extractor(self.extracted_text,"(\s|\S)*(?=Account Number)")
        self.coj_template["DueDate"] = DueDate
    
        # Get Account Number and remove text
        account_number = trim_extractor(re_extractor(self.extracted_text,"(Account Number:).*"),"(Account Number:)")
        self.coj_template["AccountNumber"] = account_number
        self.extracted_text = trim_extractor(self.extracted_text,"Account Number.*")


        # Check which services are on the invoice
        #  Property Rates
        if "property rates" in self.extracted_text.lower().replace("excluding property rates"):
            self.coj_template["isRates"] = True
            rates_section = re_extractor(self.extracted_text,"Property Rates(\s|\S)*(?=City Power| Johannesburg Water| PIKITUP)*")
            rates_VAT = re_extractor(self.extracted_text,"\d+\.\d+.*").split()
            # print(refuse)
        
        #  # Electricity
        # if "electricity" in self.extracted_text.lower():
        #     self.coj_template["isElectricity"] = True
        #     # electricity = re_extractor(self.extracted_text,"WASTE MANAGEMENT SERVICE(\s|\S)*VAT.*")
        #     # print(refuse)
        
        #  # Water&Sanitation
        # if "water & sanitation" in self.extracted_text.lower():
        #     self.coj_template["IsWaterAndSewer"] = True
        #     # water_and_sewer = re_extractor(self.extracted_text,"WASTE MANAGEMENT SERVICE(\s|\S)*VAT.*")
        #     # print(refuse)
       
        # PIKITUP
        if "pikitup" in self.extracted_text.lower():
            self.coj_template["isRefuse"] = True
            refuse = re_extractor(self.extracted_text,"WASTE MANAGEMENT SERVICE(\s|\S)*VAT.*")
            # print(refuse)
        
        #  # Sundry
        # if "Sundry" in self.extracted_text.lower():
        #     self.coj_template["isSundry"] = True
        #     refuse = re_extractor(self.extracted_text,"WASTE MANAGEMENT SERVICE(\s|\S)*VAT.*")
        #     # print(refuse)
        
        
        
        return self.extracted_text, self.coj_template
    
    
    
TEST = ExtractorCOJ()
a,b =TEST.readpdf_and_json(r"C:\Users\DonovanE\Tangent IT Solutions\TeamRPA - General\10. Client Documentation\Italtile\1. Municipality Processing\0. From Customer\Municipal_Invoices_\City of Johannesburg\CTM Bruma - 554222034(Elect_Rates_Water_Refuse).pdf")
# a,b =TEST.readpdf_and_json(r"C:\Users\DonovanE\Tangent IT Solutions\TeamRPA - General\10. Client Documentation\Italtile\1. Municipality Processing\0. From Customer\Municipal_Invoices_\City of Johannesburg\CTM Westgate 301191623  (Water_Rates_Refuse).pdf")
# print(a)

c,d = TEST.regex_into_template()
print(c)
# with open(r"C:\Users\DonovanE\Desktop\COJ2.txt","w") as f:
#     f.write(c)