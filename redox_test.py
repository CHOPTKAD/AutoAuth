import json


# Simulated endpoint function
def mock_redox_endpoint(data):
    print("✅ Received request at mock Redox endpoint.")
    print("🧾 Data Received:")
    print(json.dumps(data, indent=2))

    # Simulate success/failure based on input
    if not data["Meta"]["Destinations"]:
        return {"status": 400, "message": "Meta.Destinations is required"}

    return {
        "status": 200,
        "message": "NewPatient successfully received by Redox"
    }


# Your mock data
data = {
    "Meta": {
        "DataModel": "PatientAdmin",
        "EventType": "NewPatient",
        "Source": "AutoAuth",
        "Destinations": ["mock-destination-id"]
    },
    "Patient": {
        "Identifiers": [{
            "ID": "00001",
            "IDType": "MR"
        }],
        "Demographics": {
            "FirstName": "Timothy",
            "LastName": "Bixby",
            "DOB": "2008-01-06",
            "Sex": "Male"
        }
    }
}

# Simulate sending
response = mock_redox_endpoint(data)
print("\n📦 Mock Redox Response:")
print(response)
