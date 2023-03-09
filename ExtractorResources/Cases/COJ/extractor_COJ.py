import PyPDF2
import json
import logging
import re

#__________________________________________________________________________________________________________________________________________________________
# CANT IMPORT?
from ExtractorResources.RegExFuncs import *
# def re_extractor(text, pattern):
#         # text = text.replace("\\","\\\\")
#         result = re.search(pattern, text)
#         if result:
#             text_found = result.group(0)
#             # print(text_found)
#             return text_found.strip()
#         else:
#             print("No match")
#             return ""
        
# # Function to extract a pattern and return the match or returns no match if none found
# def trim_extractor(text, pattern):
#     text = text.replace("\\","\\\\")
#     result = re.search(pattern, text)
#     if result:
#         text_found = result.group(0)
#         # print(text_found)
#         return text.replace(text_found,"").strip()
#     else:
#         print("No match")
#         return text
    
# __________________________________________________________________________________________________________________________________________________________


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
        
        # Get Total Due
        total_due = trim_extractor(re_extractor(self.extracted_text,"Total Due \d*.*"),"Total Due").replace(",","")
        self.coj_template["TotalDue"] = total_due
        
        # Get Date and remove unwanted text up to Current Charges
        invoice_date = re_extractor(self.extracted_text,"(?!Date) \d{4}/\d{2}/\d{2}")
        self.coj_template["InvoiceDate"] = invoice_date
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
        if "property rates" in self.extracted_text.lower().replace("excluding property rates",""):
            self.coj_template["Content"]["isRates"] = True
            logging.info("Extract property rates")
            rates_section = re_extractor(self.extracted_text.lower(),"property rates(\s|\S)*(?=city power)|(?=johannesburg water)|(?=pikitup)|(?=city of johannesbug)")
            # Get money row
            rates = re_extractor(rates_section,"vat.*\d+\.\d+.*").replace(",","")
            rates_vat = re_extractor(rates,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[0]
            rates_total = re_extractor(rates,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[1]
            # Remove VAT value
            rates_excl = str(round(float(rates_total)-float(rates_vat),2))
            # Remove properties section
            self.extracted_text = self.extracted_text.replace(rates_section,"").strip()
            # Add to template
            self.coj_template["Rates"]["Total"] = rates_total
            self.coj_template["Rates"]["Total_Excl"] = rates_excl 
            self.coj_template["Rates"]["VAT"] = rates_vat
        
        # Electricity
        if "electricity" in self.extracted_text.lower():
            self.coj_template["Content"]["isElectricity"] = True
            logging.info("Extract electricity")
            electricity_section = re_extractor(self.extracted_text.lower(),"electricity(\s|\S)*(?=johannesburg water)|(?=pikitup)|(?=city of johannesbug)")
            # Get money row
            electricity = re_extractor(electricity_section,"vat.*\d+\.\d+.*").replace(",","")
            electricity_vat = re_extractor(electricity,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[0]
            electricity_total = re_extractor(electricity,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[1]
            # Remove VAT value
            electricity_excl = str(round(float(electricity_total)-float(electricity_vat),2))
            # Remove properties section
            self.extracted_text = self.extracted_text.replace(electricity_section,"").strip()
            # Add to template
            self.coj_template["Electricity"]["Total"] = electricity_total
            self.coj_template["Electricity"]["Total_Excl"] = electricity_excl 
            self.coj_template["Electricity"]["VAT"] = electricity_vat
            
         # Water&Sanitation
        
        # Water & Sanitaion
        if "water & sanitation" in self.extracted_text.lower():
            logging.info("Extract water and sanitation")
            self.coj_template["Content"]["IsWaterAndSanitaion"] = True
            water_sanitation_section = re_extractor(self.extracted_text.lower(),"water & sanitation(\s|\S)*(?=pikitup)|(?=city of johannesbug)")
            # Get money row
            water_sanitation = re_extractor(water_sanitation_section,"vat.*\d+\.\d+.*").replace(",","")
            water_sanitation_vat = re_extractor(water_sanitation,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[0]
            water_sanitation_total = re_extractor(water_sanitation,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[1]
            # Remove VAT value
            water_sanitation_excl = str(round(float(water_sanitation_total)-float(water_sanitation_vat),2))
            # Remove properties section
            self.extracted_text = self.extracted_text.replace(water_sanitation_section,"").strip()
            # Add to template
            self.coj_template["WaterAndSanitation"]["Total"] = water_sanitation_total
            self.coj_template["WaterAndSanitation"]["Total_Excl"] = water_sanitation_excl 
            self.coj_template["WaterAndSanitation"]["VAT"] = water_sanitation_vat
       
        # PIKITUP
        if "pikitup" in self.extracted_text.lower():
            self.coj_template["Content"]["isRefuse"] = True
            logging.info("Extract refuse")
            refuse_section = re_extractor(self.extracted_text.lower(),"refuse(\s|\S)*(?=city of johannesburg)")
            # Get money row
            refuse = re_extractor(refuse_section,"vat.*\d+\.\d+.*").replace(",","")
            refuse_vat = re_extractor(refuse,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[0]
            refuse_total = re_extractor(refuse,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[1]
            # Remove VAT value
            refuse_excl = str(round(float(refuse_total)-float(refuse_vat),2))
            # Remove properties section
            self.extracted_text = self.extracted_text.replace(refuse_section,"").strip()
            # Add to template
            self.coj_template["Refuse"]["Total"] = refuse_total
            self.coj_template["Refuse"]["Total_Excl"] = refuse_excl 
            self.coj_template["Refuse"]["VAT"] = refuse_vat
            
        # Sundry
        if "sundry" in self.extracted_text.lower():
            self.coj_template["Content"]["isSundry"] = True
            logging.info("Extract sundry")
            sundry_section = re_extractor(self.extracted_text.lower(),"sundry(\s|\S)*(?=current charges)")
            # Get money row
            sundry = re_extractor(sundry_section,"vat.*\d+\.\d+.*").replace(",","")
            sundry_vat = re_extractor(sundry,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[0]
            sundry_total = re_extractor(sundry,"(?!\d*\.\d*\%)\d+\.\d+.*").split(" ")[1]
            # Remove VAT value
            sundry_excl = str(round(float(sundry_total)-float(sundry_vat),2))
            # Remove properties section
            self.extracted_text = self.extracted_text.replace(sundry_section,"").strip()
            # Add to template
            self.coj_template["Sundry"]["Total"] = sundry_total
            self.coj_template["Sundry"]["Total_Excl"] = sundry_excl 
            self.coj_template["Sundry"]["VAT"] = sundry_vat
        
                
        # return self.extracted_text, self.coj_template
        return self.coj_template
    
    
    
TEST = ExtractorCOJ()
a,b =TEST.readpdf_and_json(r"C:\Users\DonovanE\Tangent IT Solutions\TeamRPA - General\10. Client Documentation\Italtile\1. Municipality Processing\0. From Customer\Municipal_Invoices_\City of Johannesburg\CTM Bruma - 554222034(Elect_Rates_Water_Refuse).pdf")
# a,b =TEST.readpdf_and_json(r"C:\Users\DonovanE\Tangent IT Solutions\TeamRPA - General\10. Client Documentation\Italtile\1. Municipality Processing\0. From Customer\Municipal_Invoices_\City of Johannesburg\CTM Westgate 301191623  (Water_Rates_Refuse).pdf")
# print(a)

c= TEST.regex_into_template()
# print(c)
# with open(r"C:\Users\DonovanE\Desktop\COJ2.txt","w") as f:
    #  f.write(str(c))