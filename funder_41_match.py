import pandas as pd
import requests
import ast


def fuzzy_funder_with_41code(funder_401_path="ror_401.csv", output_file = "fuzzy_ror_41.csv"):
    # Load the CSV file into a pandas DataFrame
    funders_df = pd.read_csv(funder_401_path)
    
    # Convert DataFrame to a list of dictionaries
    funders = funders_df.to_dict(orient='records')
    
    
    result = []
    not_found = len(funders)
    found_after = 0
    still_not_found = 0
    for funder in funders:
        #normalize the funder name and alternative name into a single list
        funderName_list = convert_name_and_alt_into_list(funder["Unique_Funder"], funder["Alternative_Name"])

        #cal the api
        url = "http://localhost:8080/api/searchfunder/fuzzy_ror"
        payload = {
            "funderName": funderName_list,
            "country": funder["Country"] if funder["Country"] != "not_found" else "",
            "region": funder["City"] if funder["City"] != "not_found" else ""
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            if data:
                found_after += 1
                result.append({
                    "Unique_Funder": funder["Unique_Funder"],
                    "Matched_Funder": data[0]["funderName"],
                    "Matched_Code": data[0]["funderId"],
                })

            else:
                still_not_found += 1
                result.append({
                    "Unique_Funder": funder["Unique_Funder"],
                    "Matched_Funder": "still_not_found",
                    "Matched_Code": "",
                })
        print(f"Processed funder: {funder['Unique_Funder']} ({found_after + still_not_found}/{not_found})")
            
    # Convert to DataFrame and save
    pd.DataFrame(result).to_csv(output_file, index=False)
    print(f"Processed {not_found} funders. Found After: {found_after}. Still Not found: {still_not_found}. Results saved to {output_file}.")


# Function to convert funder name and alternative name into a list
def convert_name_and_alt_into_list(funder_name, alternative_name):
   if alternative_name == "not_found":
         return [funder_name]
   s_fixed = alternative_name.replace('""', '"')
   new_alt = ast.literal_eval(s_fixed)
   new_alt = [funder_name] + new_alt
   return new_alt


#example
# fuzzy_funder_with_41code()