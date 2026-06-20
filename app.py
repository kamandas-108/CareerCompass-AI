import os
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app) # Enables Cross-Origin requests if frontend and backend are hosted separately

# --- DATABASE CONFIGURATION ---
# Replace this variable with your actual Neon database connection string
NEON_DB_STRING = os.environ.get("NEON_DB_STRING", "postgresql://user:password@ep-cool-butterfly-123456.us-east-2.aws.neon.tech/dbname?sslmode=require")

# --- GEMINI API CONFIGURATION ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set. API calls will fail.")

@app.route('/')
def serve_frontend():
    """Serves the main HTML file."""
    return send_file('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_profile():
    try:
        data = request.json
        interests = data.get('interests', '')
        skills = data.get('skills', '')
        subjects = data.get('subjects', '')
        traits = data.get('traits', '')

        prompt = f"""
        Analyze the following user profile and act as an expert AI career counselor.
        Interests: {interests}
        Skills: {skills}
        Favorite Subjects: {subjects}
        Personality Traits: {traits}

        Generate a JSON object exactly matching this structure. Do not use markdown blocks, return pure JSON:
        {{
          "careers": [
            {{
              "title": "Job Title",
              "suitability": 95,
              "salaryRange": "$XX,XXX - $XXX,XXX",
              "futureDemand": 90,
              "courses": ["Course 1", "Course 2"],
              "certifications": ["Cert 1", "Cert 2"],
              "youtubePlaylists": ["Playlist Idea 1", "Playlist Idea 2"],
              "roadmap": ["Beginner Step", "Intermediate Step", "Job-Ready Step"]
            }}
          ],
          "projects": {{
            "beginner": ["Idea 1", "Idea 2"],
            "intermediate": ["Idea 1", "Idea 2"],
            "portfolio": ["Suggestion 1", "Suggestion 2"]
          }}
        }}
        Limit the 'careers' array to exactly 5 top paths.
        """

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # Safely clean up potential markdown formatting from Gemini
        # This approach avoids the syntax errors caused by copy/pasting backticks
        response_text = response.text.strip()
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```", "")
        response_text = response_text.strip()

        parsed_data = json.loads(response_text)
        return jsonify(parsed_data), 200

    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return jsonify({"error": "Failed to analyze profile. Please try again."}), 500

if __name__ == '__main__':
    # Runs on port 5000 locally
    app.run(debug=True, port=5000)
