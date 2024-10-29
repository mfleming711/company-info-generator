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

words_in_title = []


def call_chatgpt_api(prompt, output_type="string"):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """
                    You are a web crawler to find the exact company information from the online sources.

                    Retrieve and verify information for the specified company with a focus on accuracy and reliability. The response should include only data that matches the highest standard of correctness, including these key business details where available:
                    Legal entity name
                    State of incorporation
                    Headquarters address
                    Revenue (approximate if exact figures are unavailable"

                    Ensure each data point is verified against multiple sources. Return only if consistent and trustworthy.
                    Do not generate any fake information.
                    Reference source example: Datanyze, ZoomInfo

                    output format:
                    #####
                    value1
                    #####
                    value2
                    #####
                    value3
                    #####
                    value4
                    #####
                """,
            },
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o",
    )
    result = response.choices[0].message.content.strip()

    if output_type == "json":
        result_dict = json.loads(result.strip())

        result_dict = {
            key.replace("_", "").lower(): value for key, value in result_dict.items()
        }
        return result_dict

    return result


def regenerate_info(company_name, retry=0):
    if retry > 3:
        print(f"Failed {company_name}")
        return []

    try:
        time.sleep(2)
        company_info_prompt = company_name

        result = call_chatgpt_api(company_info_prompt, "string")

        result = result.split("#####")

        cleaned_list = [s.strip() for s in result if s.strip()]

        product_title = cleaned_list[0]
        title_p = product_title.split(" ")

        result_dict = [
            [
                company_name,
                cleaned_list[0],
                cleaned_list[1],
                cleaned_list[2],
                cleaned_list[3],
            ]
        ]

        return result_dict
    except Exception as e:
        time.sleep(1)
        regenerate_info(company_name, retry + 1)
        return []


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
