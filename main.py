import os
import json
import uuid
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
saved_sessions = {}  # In-memory session store


@app.route("/")
def home():
    return render_template("covermymeds.html")


@app.route("/covermymed")
def covermymed():
    return render_template("covermymeds.html")


@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        content = request.get_json()
        session_id = content.get("session_id", str(uuid.uuid4()))

        if "ehr_json" in content:
            prompt_input = json.dumps(content["ehr_json"], indent=2)
        else:
            prompt_input = content.get("input", "")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a prior authorization assistant for a clinical AI tool.\n"
                        "Extract structured information from raw patient EHR JSON.\n"
                        "Return only valid JSON with the following keys:\n"
                        "- full_name, DOB, age, sex\n"
                        "- conditions (array), medications (array), allergies (array)\n"
                        "- provider_name, clinic, provider_phone, npi\n"
                        "- insurance_name, insurance_id, group_number\n"
                        "- prior_treatments (array), reason_for_request\n"
                        "- follow_up (object with PA-related questions answered)\n\n"
                        "For follow_up, generate relevant prior authorization questions based on the patient data, such as:\n"
                        "- 'has_patient_tried_first_line_therapy': 'Yes/No with details'\n"
                        "- 'contraindications_to_alternatives': 'Any contraindications explained'\n"
                        "- 'duration_of_current_treatment': 'How long patient has been on current therapy'\n"
                        "- 'clinical_response_to_previous_meds': 'Response to prior medications'\n"
                        "- 'severity_of_condition': 'Mild/Moderate/Severe with justification'\n"
                        "Generate 3-5 relevant questions based on the specific patient case.\n\n"
                        "If a field is missing, set it to 'Not provided'.\n"
                        "DO NOT include explanations or text outside the JSON.\n"
                        "Your entire output must be one valid JSON object only."
                    )
                },
                { "role": "user", "content": prompt_input }
            ]
        )

        ai_reply = response.choices[0].message.content

        try:
            structured = json.loads(ai_reply)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON from AI", "status": 500})

        saved_sessions[session_id] = structured

        return jsonify({
            "message": "AI structured output received.",
            "output": structured,
            "session_id": session_id,
            "status": 200
        })

    except Exception as e:
        return jsonify({"error": str(e), "status": 500})


@app.route("/sessions", methods=["GET"])
def list_sessions():
    return jsonify(list(saved_sessions.keys()))


@app.route("/session/<session_id>", methods=["GET"])
def get_session(session_id):
    return jsonify(saved_sessions.get(session_id, {}))


@app.route("/export/json/<session_id>", methods=["GET"])
def export_json(session_id):
    data = saved_sessions.get(session_id)
    if not data:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(data)


@app.route("/export/pdf/<session_id>")
def export_pdf(session_id):
    return "PDF export feature coming soon.", 501


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
