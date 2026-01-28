## How to run the project

### 1. Activate virtual environment
venv\Scripts\activate

### 2. Install requirements
pip install -r requirements.txt

### 3. Run backend
uvicorn app.main:app --reload

### 4. Run frontend
streamlit run gui/streamlit_app.py
