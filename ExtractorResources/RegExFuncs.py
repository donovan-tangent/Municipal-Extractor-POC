import re

# Function to extract a pattern and return the match or returns no match if none found
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
    