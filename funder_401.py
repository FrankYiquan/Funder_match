import pandas as pd
import json
import requests

def funder_with_401code(unique_funder_path="unique_funders.json", funder_401_path="funder_401.csv", output_path="funder_with_401code.csv"):
    # Load funder names from JSON list
    with open(unique_funder_path, 'r', encoding='utf-8') as f:
        unique_funders = json.load(f)

    funder_401 = pd.read_csv(funder_401_path)

    results = []
    not_found_count = 0
    total_funders = len(unique_funders)

    for name in unique_funders:
        # Match using exact string (case sensitive)
        matched = funder_401[funder_401["Name"].str.contains(name, na=False, case=False)]

        if not matched.empty:
            # Take the first matching row
            first_match = matched.iloc[0]
            results.append({
                "Name": name,
                "Code": first_match["Code"]
            })
        else:
            # If no match, return "not_found"
            not_found_count += 1
            results.append({
                "Name": name,
                "Code": "not_found"
            })

    # Convert to DataFrame and save
    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"Processed {total_funders} funders. Not found: {not_found_count}. Results saved to {output_path}.")

def fuzzy_funder_with_401code(funder_401_path="funder_with_401code.csv", output_file = "fuzzy_401.csv"):
    # Load the CSV file into a pandas DataFrame
    funders_df = pd.read_csv(funder_401_path)
    
    # Convert DataFrame to a list of dictionaries
    funders = funders_df.to_dict(orient='records')
    
    
    result = []
    not_found = len(funders)
    found_after = 0
    still_not_found = 0
    for funder in funders:
        if funder["Code"] == "not_found":
            #cal the api
            url =  f"http://localhost:8080/api/searchfunder/fuzzy?funderName={funder['Name']}"
            response = requests.get(url)    
            if response.status_code == 200:
                data = response.json()
                if data:
                    found_after += 1
                    result.append({
                        "Unique_Funder": funder["Name"],
                        "Matched_Funder": data[0]["funderName"],
                        "Matched_Code": data[0]["funderId"],
                        "Reliable(Y/N)": ""
                    })
                else:
                    still_not_found += 1
                    result.append({
                        "Unique_Funder": funder["Name"],
                        "Matched_Funder": "still_not_found",
                        "Matched_Code": "",
                        "Reliable(Y/N)": ""
                    })
                
    # Convert to DataFrame and save
    pd.DataFrame(result).to_csv(output_file, index=False)
    print(f"Processed {not_found} funders. Found After: {found_after}. Still Not found: {still_not_found}. Results saved to {output_file}.")


#example

#fuzzy_funder_with_401code()

funder_with_401code()


    


    