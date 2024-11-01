from openai import OpenAI
import csv
import json
import time

# Set your OpenAI API key
OPENAI_API_KEY = (
    "sk-proj-AbPkTpSxp**********************BSaeisjgezLIeH"  # Replace your key here
)

client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)

functions = [
    {
        "name": "get_company_info",
        "description": """
                    You are a web crawler to find the exact company information from the online sources.

                    Collect and verify the specified company's information with a strict focus on accuracy. Each piece of data should meet high standards for reliability, and the following key business details should be included if available:
                    - Legal entity name: Ensure the full, registered name is returned, including the company type at the end (e.g., Inc, LLC, Co).
                    - State of incorporation
                    - Headquarters address: Include the full address, such as street, city, zip code, and state.
                    - Revenue: Provide an approximate figure if exact numbers are not available.

                    Ensure each data point is verified against multiple sources. Return only if consistent and trustworthy.
                    Do not generate any fake information.
                    Reference source example: Datanyze, ZoomInfo
                """,
        "parameters": {
            "type": "object",
            "properties": {
                "legal_entity_name_with_entity_type": {
                    "type": "string",
                    "description": "Entity type must be included",
                },
                "state": {
                    "type": "string",
                    "description": "The state of incorporation is the state where a business is registered to become a separate legal entity.",
                },
                "hq_address": {
                    "type": "string",
                    "description": "An HQ address is the address of a company's headquarters, which is the main office where the executive management and key staff are located.",
                },
                "revenue": {
                    "type": "string",
                    "description": "The approximate revenue of the company.",
                },
            },
            "required": [
                "legal_entity_name_with_entity_type",
                "state",
                "hq_address",
                "revenue",
            ],
        },
    }
]


def call_chatgpt_function(company_name):
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {
                "role": "user",
                "content": f"Retrieve company information for {company_name}",
            }
        ],
        functions=functions,
        function_call={"name": "get_company_info"},
    )

    # Extracting the output
    function_response = json.loads(response.choices[0].message.function_call.arguments)

    return function_response


def regenerate_info(company_name, retry=0):
    try:
        time.sleep(2)
        if retry > 0:
            print(f'Retrying "{company_name}"')
        else:
            print(f'Analyzing "{company_name}"')

        result = call_chatgpt_function(company_name)

        # validate the result
        if len(result["legal_entity_name_with_entity_type"]) == 0:
            raise "Company name is invalid"
        if len(result["state"]) == 0:
            raise "State is invalid"
        if len(result["hq_address"]) == 0:
            raise "HQ address is invalid"
        if len(result["revenue"]) == 0:
            raise "Revenue is invalid"

        result_dict = [
            [
                company_name,
                result["legal_entity_name_with_entity_type"],
                result["state"],
                result["hq_address"],
                result["revenue"],
            ]
        ]

        return result_dict
    except Exception as e:
        time.sleep(1)
        if retry > 2:
            print(f'Failed "{company_name}"')
            return []
        retried = regenerate_info(company_name, retry + 1)
        return retried


def read_products_from_csv(file_path):
    products = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            products.append(row)
    return products


def write_products_to_csv(products, file_path):
    with open(file_path, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write the new rows
        writer.writerows(products)


def main(input_csv, output_csv):
    companies = read_products_from_csv(input_csv)

    for company in companies:
        new_product = regenerate_info(company["name"])

        write_products_to_csv(new_product, output_csv)

    print(f"Updated product data saved to {output_csv}")


if __name__ == "__main__":
    input_csv = "company_list.csv"  # Input CSV file path
    output_csv = "full_company_info.csv"  # Output CSV file path
    main(input_csv, output_csv)
