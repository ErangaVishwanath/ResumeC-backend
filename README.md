# Resume Verifier API

This project is a FastAPI application designed to verify resumes by extracting skills from uploaded PDF files and matching them with a user's GitHub repositories. It also provides a question bank for technical interviews based on the candidate's technology stack.

## Project Structure

```
resumeC
├── app
│   ├── main.py            # FastAPI application with endpoints for resume verification and question fetching
│   └── QuestionBank.csv   # CSV file containing interview questions and expected answers
├── requirements.txt       # Python dependencies required for the project
└── README.md              # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd resumeC
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Usage

1. **Run the FastAPI application:**
   ```
   uvicorn app.main:app --reload
   ```

2. **Access the API documentation:**
   Open your browser and navigate to `http://localhost:8000/docs` to view the interactive API documentation.

## Endpoints

- **POST /verify_resume/**: Upload a resume PDF and a GitHub username to verify skills.
- **POST /get-questions**: Retrieve interview questions based on the specified technology stack and difficulty level.
- **POST /check-answer**: Check the similarity of a candidate's answer against the expected answer from the question bank.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.