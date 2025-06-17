
# MedAI – AI-Powered Medical Chatbot & Disease Predictor

MedAI is a real-time AI assistant that interacts with users through chat, predicts possible diseases based on their symptoms, and provides useful health guidance.

---

## Features

- **Real-Time Symptom-Based Prediction**  
  Uses **K‑Nearest Neighbors (KNN)** to predict diseases from user-reported symptoms via a responsive chat interface.

- **Natural Language Understanding**  
  Incorporates **NLP techniques** (NLTK and custom parsing) for symptom interpretation and clarification during conversation.

- **Health Recommendations**  
  Suggests disease-related information, precautions, and initial care steps based on predicted outcomes.

- **Modular Architecture**  
  - `ChatClass.py` for managing dialogue  
  - `PredictDiseases.py` for KNN-based prediction  
  - `NlpClass.py`, `SemanticClass.py`, `SyntacticClass.py` for handling user input  
  - `__main__.py` handles real-time WebSocket communication and server startup logic

- **Future-Capable**  
  Infrastructure designed to support **CNN-based image diagnosis** for visual symptoms.

---

## Project Structure

```
/
├── Constants/
│   └── path.py
│
├── core/
│   ├── ChatClass.py
│   ├── ImageToSymptoms.py
│   ├── NlpClass.py
│   ├── PredictDiseases.py
│   ├── SemanticClass.py
│   ├── ServerMgmtClass.py
│   └── SyntacticClass.py
│
├── Dataset/
│   ├── imagedataset/
│   ├── cleanDataset.csv
│   ├── cleanDataset.pkl
│   ├── Dataset.csv
│   ├── SymDescriptions.csv
│   ├── symptom_Description.csv
│   ├── symptom_precaution.csv
│   ├── Symptom_serverity.csv
│   └── Dataset.csv
│
├── logs/
│   └── log.txt
│
├── Storage/
│   ├── SavedData/
│   ├── Savedencoders/
│   ├── SavedModels/
│   └── UserData/
│
├── templates/
│   └── testingws.html
│
├── __init__.py
├── __main__.py
├── README.md
└── requirements.txt
```

---

## Tech Stack

- **Backend**: Python, FastAPI, Socket.IO  
- **ML/NLP**: Scikit‑learn (KNN), NLTK  
- **Frontend**: React, WebSocket (via `useSocket.tsx`)  
- **Data**: Custom CSVs for symptoms, precautions, and disease info  
- **(Planned)**: TensorFlow-based CNN integration for image analysis

---

## Required Folders (External)

To run this project correctly, please download and extract the following folders into the root directory of the project (i.e., they should be siblings to the `core/` or `medaibackend/` folder):

- **Datasets Folder**  
  [Download Datasets.zip](https://drive.google.com/file/d/1rsxa99DE4Org9SgPEVNNH2W8Fs-_UzDM/view?usp=sharing)  
  → Extract to: `./Datasets/`

- **Storage Folder**  
  [Download Storage.zip](https://drive.google.com/file/d/1NR4hHNTIPPmOtbfaoE6jb-Kti64JB7oR/view?usp=sharing)  
  → Extract to: `./Storage/`

**Important:** Make sure both folders are placed directly inside the project root, not inside any subfolder, to ensure proper path access by the code.

---

## Setup & Usage

1. **Clone the repository**
   ```bash
   git clone https://github.com/UditSax3na/MedAi-backend.git
   cd MedAi-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux or macOS
   ./venv/Scripts/activate   # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend**
   ```bash
   uvicorn app:app --reload
   ```

5. **Start the frontend client**  
   (Refer to `Chat.tsx`/`useSocket.tsx` for connection settings.)

---

## Planned Enhancements

- Add **CNN-based image recognition** to support visual symptom detection.  
- Expand **disease database** for improved accuracy and broader coverage.  
- Build a **user profile system** to track symptom history and predictions over time.

---

## Contributing

Contributions are welcome! Feel free to open an issue or pull request—especially if you'd like to help with CNN/image functionality or expanding the disease database.

---

## Author

**Udit Saxena** – AI/ML & Backend Developer  
- GitHub: [UditSax3na](https://github.com/UditSax3na)  
- LinkedIn: [https://www.linkedin.com/in/uditsax3na](https://www.linkedin.com/in/uditsax3na)  

---

## Frontend Developer

**Rohit Vishwakarma** – Developed the full frontend interface  
- GitHub: [Rohit Vishwakarma](https://github.com/Shad0wcoder)  
- Frontend Repo: [https://github.com/Shad0wcoder/medai1](https://github.com/Shad0wcoder/medai1)

---