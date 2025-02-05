import requests
import csv

# Set up GraphQL endpoint and query
URL = "https://app.traceable.ai/graphql"
QUERY = {
    "query": """
    {
      dataSets {
        results {
          id
          name
          description
          enabled
          dataSuppression
          dataTypes {
            id
            name
            description
            scopedPatterns {
              locations
              patternType
              matchType
              scope {
                type
                environmentScope {
                  environmentIds
                  __typename
                }
                __typename
              }
              keyPattern {
                operator
                value
                __typename
              }
              valuePattern {
                operator
                value
                __typename
              }
              __typename
            }
            __typename
          }
          sensitivity
          color
          __typename
        }
      }
    }
    """
}

# Replace <JWT> with your JWT token
HEADERS = {
    "Authorization": "Bearer <enterYourPrivateJWTToken>",
    "Content-Type": "application/json"
}

# Send the request
response = requests.post(URL, json=QUERY, headers=HEADERS)

# Check for valid response
if response.status_code == 200:
    response_json = response.json()

    # Check if the response JSON contains the expected keys and is not None
    if response_json and "data" in response_json and "dataSets" in response_json["data"] and "results" in \
            response_json["data"]["dataSets"]:
        data_sets = response_json["data"]["dataSets"]["results"]
    else:
        print("Unexpected response structure or empty results.")
        exit()

    # Extracting data and writing to CSV
    with open("output.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # Define CSV header
        writer.writerow([
            "DataSet ID", "DataSet Name", "DataType ID", "DataType Name", "DataType Description",
            "ScopedPattern Locations", "ScopedPattern PatternType", "ScopedPattern MatchType",
            "Scope Type", "EnvironmentScope IDs", "KeyPattern Operator", "KeyPattern Value",
            "ValuePattern Operator", "ValuePattern Value"
        ])

        for data_set in data_sets:
            for data_type in data_set["dataTypes"]:
                for scoped_pattern in data_type["scopedPatterns"]:
                    # Extracting scope and environmentScope
                    scope_type = scoped_pattern["scope"]["type"] if scoped_pattern["scope"] else None
                    environment_ids = scoped_pattern["scope"]["environmentScope"]["environmentIds"] if scoped_pattern[
                                                                                                           "scope"] and \
                                                                                                       scoped_pattern[
                                                                                                           "scope"].get(
                                                                                                           "environmentScope") else None

                    # Extracting keyPattern and valuePattern
                    key_operator = scoped_pattern["keyPattern"]["operator"] if scoped_pattern["keyPattern"] else None
                    key_value = scoped_pattern["keyPattern"]["value"] if scoped_pattern["keyPattern"] else None
                    value_operator = scoped_pattern["valuePattern"]["operator"] if scoped_pattern[
                        "valuePattern"] else None
                    value_value = scoped_pattern["valuePattern"]["value"] if scoped_pattern["valuePattern"] else None

                    writer.writerow([
                        data_set["id"],
                        data_set["name"],
                        data_type["id"],
                        data_type["name"],
                        data_type.get("description", ""),
                        ", ".join(scoped_pattern["locations"]),
                        scoped_pattern["patternType"],
                        scoped_pattern["matchType"],
                        scope_type,
                        ", ".join(environment_ids) if environment_ids else None,
                        key_operator,
                        key_value,
                        value_operator,
                        value_value
                    ])

    print("Data written to output.csv")

else:
    print(f"Failed with status code: {response.status_code}")
