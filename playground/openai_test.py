import json
import time
import openai
import requests

# Define the Goldilocks API base URL
GOLDILOCKS_API_BASE = "http://localhost:8000"
user_id = "chris.chiuwing.cheung@gmail.com"
spreadsheet_id = "1Phjx9vyRe2aF1_wlsogLHT6AK6VYXzcy87Dp3V5_RWE"

openai_functions = [
  {
      "name": "generate_auth_url",
      "description": "Generate OAuth authorization URL for End User",
      "parameters": {
          "type": "object",
          "properties": {
              "user_id": {
                  "type": "string",
                  "description": "Unique identifier for the End User."
              }
          },
          "required": ["user_id"]
      }
  },
  {
      "name": "read_spreadsheet",
      "description": "Read values from a Google Sheet.",
      "parameters": {
          "type": "object",
          "properties": {
              "user_id": {"type": "string", "description": "End User's unique identifier."},
              "spreadsheet_id": {"type": "string", "description": "Google Sheet ID."},
              "range_name": {"type": "string", "description": "Range to read, e.g., 'Sheet1!A1:B10'."}
          },
          "required": ["user_id", "spreadsheet_id", "range_name"]
      }
  },
  {
      "name": "update_spreadsheet",
      "description": "Update values in a Google Sheet.",
      "parameters": {
          "type": "object",
          "properties": {
              "user_id": {"type": "string", "description": "End User's unique identifier."},
              "spreadsheet_id": {"type": "string", "description": "Google Sheet ID."},
              "range_name": {"type": "string", "description": "Range to update, e.g., 'Sheet1!C1:D2'."},
              "data": {
                  "type": "array",
                  "description": "Values to write, in a 2D array.",
                  "items": {"type": "array", "items": {"type": "string"}}
              }
          },
          "required": ["user_id", "spreadsheet_id", "range_name", "data"]
      }
  }
]

def generate_auth_url(args):
  user_id = args["user_id"]
  response = requests.get(f"{GOLDILOCKS_API_BASE}/google/auth_url", params={"user_id": user_id})
  if response.status_code == 200:
      return response.json()["auth_url"]
  else:
      raise Exception("Failed to generate authorization URL.")
  
def poll_auth_status(user_id):
  authorized = False
  count = 0
  while authorized is False and count < 30:
    response = requests.get("http://localhost:8000/google/auth_status", params={"user_id": user_id})
    if response.status_code == 200 and response.json()["authorized"]:
        print("Authorization completed!")
        authorized = True
    else:
        print("Waiting for End User to authorize...")
    time.sleep(2)  # Poll every 2 seconds
    count += 1
  return authorized
  
def read_spreadsheet(args):
  user_id = args["user_id"]
  spreadsheet_id = args["spreadsheet_id"]
  range_name = args["range_name"]
  response = requests.get(
    f"{GOLDILOCKS_API_BASE}/google/read",
    params={"user_id": user_id, "spreadsheet_id": spreadsheet_id, "range_name": range_name}
  )
  if response.status_code == 200:
    return response.json()
  else:
    raise Exception("Failed to read spreadsheet data.")

def update_spreadsheet(args):
    user_id = args["user_id"]
    spreadsheet_id = args["spreadsheet_id"]
    range_name = args["range_name"]
    values = args["values"]
    response = requests.post(
      f"{GOLDILOCKS_API_BASE}/google/update",
      params={"user_id": user_id, "spreadsheet_id": spreadsheet_id, "range_name": range_name},
      json={"values": values}
    )
    if response.status_code == 200:
      return response.json()
    else:
      raise Exception("Failed to update spreadsheet data.")
   
def simulate_openai_workflow():
    # Step 1: Generate Auth URL
    # generate_response = openai.ChatCompletion.create(
    #     model="o1-mini",
    #     messages=[{"role": "user", "content": f"Generate OAuth URL for user {user_id}."}],
    #     functions=openai_functions,
    #     function_call={"name": "generate_auth_url"}
    # )
    # auth_url = generate_auth_url({"user_id": user_id})
    # print("Auth URL:", auth_url)

    # if poll_auth_status(user_id) is False:
    #     print("Authorization not completed. Exiting...")
    #     return

    # Step 2: Read from Spreadsheet
    read_response = openai.ChatCompletion.create(
        model="o1-mini",
        messages=[{"role": "user", "content": f"Read values from '{spreadsheet_id}', range 'Sheet1!A1:B10'."}],
        functions=openai_functions,
        function_call={"name": "read_spreadsheet"}
    )
    read_result = read_spreadsheet({"user_id": user_id, "spreadsheet_id": spreadsheet_id, "range_name": "Sheet1!A1:B10"})
    print("Read Result:", read_result)

    # Step 3: Update Spreadsheet
    update_response = openai.ChatCompletion.create(
        model="o1-mini",
        messages=[{"role": "user", "content": f"Update '{spreadsheet_id}', range 'Sheet1!C1:D2' with [['Hello', 'World'], ['More', 'Data']]."}],
        functions=openai_functions,
        function_call={"name": "update_spreadsheet"}
    )
    update_result = update_spreadsheet({
      "user_id": user_id,
      "spreadsheet_id": spreadsheet_id,
      "range_name": "Sheet1!C1:D2",
      "values": [["Hello", "World"], ["More", "Data"]]
    })
    print("Update Result:", update_result)



def main():
  simulate_openai_workflow()

if __name__ == "__main__":
    main()
  


  
