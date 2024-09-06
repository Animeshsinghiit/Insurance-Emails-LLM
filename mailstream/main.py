import streamlit as st
from openai import OpenAI
from sample_dataset import dataset
from categories import email_categories

import json
import re
openai = OpenAI(
    api_key="zwxEF8eh280G8z2sSVzxEij9",
    base_url="https://cloud.olakrutrim.com/v1",
)

def get_email_category(email_categories,input_email):
  
  # print(1)
    categorisation_prompt = f"""
You are an expert AI agent with advanced knowledge in analyzing **emails** and accurately categorizing them into specific insurance-related categories. Your role is to ensure that each email is assigned to the most appropriate category based on its content, context, and intent.

<knowledge>
- All emails are sent by customers to an Insurance company.
- Emails may vary in tone, structure, and complexity, ranging from simple inquiries to detailed requests.
- Customers may include multiple requests or concerns in a single email, and it's your task to identify the primary intent.
- Some emails may contain ambiguous language, requiring you to infer the correct category based on context and industry knowledge.
- Consider edge cases where emails may reference industry-specific terminology, abbreviations, or jargon that are typical within the insurance sector.
- The sender's intent might not always align with the explicit content of the email, and you should prioritize the core objective of the communication.
- Certain categories might overlap, but your task is to determine the best match that reflects the email's main purpose.
- Be aware of the possibility of emails related to new, unlisted categories, and handle them with the appropriate classification or flagging mechanism.
</knowledge>

<Input Email>
{input_email}
<Input Email/>

<Output Format>
- Always return a JSON object with the following keys:
    - `category`: 
        - Identify the category of the email from the provided list of categories in the categories dictionary.
        - Ensure the selected category reflects the primary focus or intent of the email.
        - If the email fits multiple categories, select the one that best aligns with the core content.
        - The category must be one of the entries from the provided categories dictionary. If no category fits, consider flagging it for review.

    - `explanation`: 
        - Provide a concise but thorough explanation for why the email was assigned to the chosen category.
        - Reference specific phrases, keywords, or contextual clues from the email that influenced the categorization.

    - `summary`: 
        - Generate a clear and concise summary that captures the essence of the email.
        - Highlight the main request, issue, or inquiry raised by the customer, avoiding unnecessary details.

    - `customer name`: 
        - Extract the customer's name, typically found at the end of the email or in the salutation.
        - Cross-reference common Indian names or personal names to ensure accuracy.

    - `mobile no`: 
        - Identify and extract the customer's mobile number from the email content.
        - Ensure the number is valid and formatted correctly, considering typical formats used in India.

    - `email id`: 
        - Locate and extract the customer's email address, typically indicated by the `@` symbol.
        - Ensure the email is valid and properly formatted.

    - `Aadhaar No`: 
        - Search for and extract the Aadhaar number, which is a unique identifier used in India.
        - Validate the number against the standard Aadhaar format (12 digits).

    - `PAN No`: 
        - Identify and extract the customer's PAN (Permanent Account Number) if mentioned.
        - Validate the PAN against the standard Indian format (5 letters, 4 digits, 1 letter).

    - `policy no`: 
        - Extract the policy number mentioned in the email.
        - Ensure the number is complete and accurately reflects the customer's policy.

    - `policy expiration date`: 
        - Identify and extract the expiration date of the policy, if mentioned.
        - Ensure the date is in a recognizable format (e.g., DD/MM/YYYY) and valid.

    - `vehicle no`: 
        - If the email pertains to vehicle insurance, extract the vehicle number or registration number.
        - Ensure the vehicle number matches standard formats used in India.

    - `policy coverage`: 
        - Determine whether the policy coverage is first-party or third-party based on the email content.
        - Clearly specify the type of coverage mentioned or implied in the email.

    - `category of damage`: 
        - If the email relates to vehicle damage, categorize it as either personal vehicle damage or third-party damage.
        - Consider any details provided about the nature of the damage to make an accurate determination.
            
- If the email could reasonably fit into multiple categories, select the most relevant one based on the email's primary focus.
- Ensure that the output is structured, clear, and ready for automated processing within the company's systems.
- Only return the JSON object and nothing else.
- Only return the latest email category.
- Before categorizing the email in a certain category, always go through the categories along with their detailed descriptions:
<categories>
{email_categories}
<categories/>

<Output Format/>

output:
"""

    # print(categorisation_prompt)
    chat_completion = openai.chat.completions.create(
        model="Meta-Llama-3-8B-Instruct",
        messages=[{"role": "user", "content": categorisation_prompt}],

        temperature= 0,

    )
    return chat_completion.choices[0].message.content


def extract_json(output_str):
    # Use regex to find the JSON block in the string
    match = re.search(r'(\{.*\})', output_str, re.DOTALL)
    if match:
        # Extract the JSON string
        json_str = match.group(1)
        
        # Clean up the JSON string
        json_str = json_str.replace('\n', '')  # Remove newline characters
        json_str = json_str.replace('“', '"').replace('”', '"')  # Replace any fancy quotes with standard quotes
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas before closing braces
        
        try:
            # Attempt to parse the cleaned JSON string
            json_obj = json.loads(json_str)
            return json_obj
        except json.JSONDecodeError as e:
            raise ValueError(f"Extracted string is not valid JSON: {e}")
    else:
        raise ValueError("No JSON found in the input string")
    


st.title("Insurance Email Categorization")
st.write("This app categorizes emails into specific insurance-related categories using AI.")


with st.sidebar:
    st.title("MailStream.AI")
    st.info("PoC Version 1")
st.header("Input Email")
input_email = st.text_area("Enter the email content here:")


if st.button("Categorize Email"):

    if input_email:
        with st.spinner("Categorizing email..."):
            output = get_email_category(email_categories, input_email)
            try:
                result = extract_json(output)
                st.success("Email categorized successfully!")
                st.json(result)
            except ValueError as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter an email content to categorize.")


st.sidebar.header("Email Categories")
st.sidebar.write(email_categories)

st.write("---")
st.write("Developed by **Zourner**")
# st.sidebar.write("---")
# st.sidebar.write("Developed by **Zourner**")
