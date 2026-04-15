# 🏥 Medical Report Diagnosis


This is the **FastAPI-based backend** for the **Medical Diagnosis Application**, which provides authentication, PDF report upload, AI-powered medical diagnosis using LLaMA 3 via Groq API, and stores metadata in MongoDB with Pinecone for vector storage.

---

## 📸 Screenshots & Demo

| Feature                                   | Screenshot                                          |
| ----------------------------------------- | --------------------------------------------------- |
| **Home Page**                             | ![Home Screenshot](/assets/homepage.png)            |
| **Report Upload / Doctor Diagnosis View** | ![Upload Screenshot](/assets/patientDashboard.png)  |
| **Doctor Diagnosis View**                 | ![Diagnosis Screenshot](/assets/doctorDahboard.png) |

📄 **Sample PDF Report:** [Download Here](/assets/sample-report.pdf)

📄 **Project Report:** [Download Here](/assets/ProjectReport.pdf)

---

## 🚀 Core Features

✅ **Role-based Authentication** ( Doctor / Patient)

✅ **PDF Report Upload**

✅ **Text Extraction & Chunking** from PDFs

✅ **AI Diagnosis Generation** using **Groq LLaMA 3**

✅ **Vector Storage with Pinecone** for RAG retrieval

✅ **MongoDB Integration** for user, report, and diagnosis records

✅ **Role-based Access Control** for viewing and requesting diagnoses

---

## 🛠 Tech Stack

- **Backend Framework:** FastAPI
- **Database:** MongoDB
- **Vector DB:** Pinecone
- **LLM API:** Groq (LLaMA 3)
- **PDF Processing:** PyPDF2
- **Environment Management:** Python 3.10+

---

## 📂 Project Structure

```

|medicalReportDiagnosis/
├── assets/
├── client/
│   ├── app.py
│   ├── .env
│   ├── requirements.txt
├── server/
│   ├── __init__.py
│   ├── main.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── services.py
│   ├── config/
│   │   └── db.py
│   ├── diagnosis/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── query.py
│   └── reports/
│       ├── __init__.py
│       ├── routes.py
│       └── services.py
├── .env
├── requirements.txt
└── .gitignore

```

---

## ⚙️ Setup Instructions (Local)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/snsupratim/MedicalReportDiagnosis.git
cd MedicalReportDiagnosis
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file and add:

```
MONGO_URI=
DB_NAME=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
PINECONE_ENV=
GOOGLE_API_KEY=
GROQ_API_KEY=
UPLOAD_DIR=
API_URL=

```

### 5️⃣ Run the Application

```bash
uvicorn server.main:app --reload
```

API will be available at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## ▶️ API Endpoints

| Method | Endpoint                     | Description           |
| ------ | ---------------------------- | --------------------- |
| POST   | `/auth/signup`               | Register a new user   |
| POST   | `/auth/login`                | Login user            |
| POST   | `/reports/upload`            | Upload medical report |
| POST   | `/diagnosis/from_report`     | Request AI diagnosis  |
| GET    | `/diagnosis/by_patient_name` | View past diagnoses   |

---

## 🔮 Future Enhancements

- ✅ **JWT Authentication** for better security
- ✅ **Streamlit Frontend Integration**
- ✅ **Advanced Analytics Dashboard for Doctors**
- ✅ **Support for Multiple File Formats (Images, DICOM)**
- ✅ **Offline PDF Processing Mode**

---
