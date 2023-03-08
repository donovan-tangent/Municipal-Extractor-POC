import re

# Function to extract a pattern and return the match or returns no match if none found
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
    
def main():
    
    # RE_Extractor()
    # Trim_Extractor()
    pass

if __name__ == '__main__':
    main()