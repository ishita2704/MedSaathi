# 🏥 MedSaathi - AI Medical Report Diagnosis

This is the **FastAPI-based backend** for the **Medical Diagnosis Application**, which enables AI-powered analysis of **medical images such as CT scans and X-rays**.

The system supports secure authentication, image upload, and intelligent diagnosis generation using **Gemini Vision AI**, while storing metadata in **MongoDB** and leveraging **Pinecone** for efficient vector-based retrieval.

It is designed to assist in identifying conditions (e.g., brain tumors, lung abnormalities) from medical imaging data and streamline doctor–patient workflows.

- 📄 `PDF/TXT reports` using **RAG + Pinecone + Groq**
- 🩻 `CT scan / X-ray images` using **Gemini Vision**

It also includes 👨‍⚕️ role-based access for doctors to view patient diagnosis history.

---

## 📸 Screenshots & Demo

| Feature | Preview |
| --- | --- |
| 🏠 **Home Page** | ![Home Page](/assets/homepage.png) |
| 🧠 **Brain Tumor Input Image** | ![Brain Tumor Input](/assets/brain%20tumor.jpg) |
| 🧠 **Brain Tumor Report Screen** | ![Brain Tumor Report](/assets/brain_tumor_report.png) |
| 🧠 **Brain Tumor Result Screen** | ![Brain Tumor Result](/assets/brain_tumor_model_result.png) |
| 🫁 **Pulmonary Lung CT Input Image** | ![Pulmonary Lung CT Input](/assets/lungs%20pulmonary%20disease.png) |
| 🫁 **Pulmonary Lung CT Report Screen** | ![Pulmonary Lung CT Report](/assets/pulmonary_lung_disease_report.png) |
| 🫁 **Pulmonary Lung CT Result Screen** | ![Pulmonary Lung CT Result](/assets/pulmonary_lung_disease_result.png) |
| 🩻 **Lungs X-ray Input Image** | ![Lungs Xray Input](/assets/lungs_xray.png) |
| 🩻 **Lungs X-ray Result Screen** | ![Lungs Xray Result](/assets/lungs_xray_result.png) |
| 🩻 **Normal Lungs X-ray Sample** | ![Normal Lungs Xray Sample](/assets/normal%20lungsXray.jpeg) |
| 🦠 **Tuberculosis X-ray Sample** | ![Tuberculosis Xray Sample](/assets/TuberculosisXray.png) |

📄 **Sample PDF Report:** [View Sample Report](/assets/sample-report.pdf)

📄 **Additional Report:** [View Report 1](/assets/report1.pdf)

📄 **Project Report:** [View Project Report](/assets/ProjectReport.pdf)

---

## 🚀 Project Overview

This project was built to simplify medical document understanding for patients and provide a quick review workflow for doctors.

### ✅ What it does
- Allows `patients` to upload medical reports
- Generates AI-based structured diagnosis responses
- Supports both `text reports` and `image-based scans`
- Saves diagnosis history for doctor review
- Enforces `role-based authentication`

---

## ✨ Core Features

- 🔐 **Role-based Authentication**
  - Separate access for `patient` and `doctor`

- 📄 **PDF/TXT Report Upload**
  - Upload one or more medical reports

- 🧠 **Text-based Diagnosis with RAG**
  - Report text is chunked, embedded, stored in Pinecone, and retrieved semantically

- 🩻 **Image-based Diagnosis**
  - Supports one CT image and one X-ray image in `PNG/JPG/JPEG`
  - Uses Gemini Vision for visual analysis

- 🗂 **Diagnosis History**
  - Saves answers, questions, sources, and timestamps in MongoDB

- 👨‍⚕️ **Doctor Dashboard**
  - Doctors can search patient records and review prior diagnoses

---

## 🛠 Tech Stack

- ⚡ **FastAPI** - backend API framework
- 🎨 **Streamlit** - frontend dashboard
- 🍃 **MongoDB** - database for users, uploads, and diagnosis history
- 📌 **Pinecone** - vector database for semantic retrieval
- 🔗 **LangChain** - text chunking and embedding pipeline
- 🚀 **Groq** - final text diagnosis generation for reports
- 🤖 **Google Gemini** - embeddings + vision-based diagnosis for images
- 🐍 **Python** - core language for frontend and backend

---

## 🧠 How It Works

### 1️⃣ Authentication & RBAC
- Users sign up and log in as either `patient` or `doctor`
- Only patients can upload reports and request diagnosis
- Doctors can only view stored patient diagnosis records

### 2️⃣ Upload Flow
When a patient uploads data:

- A unique `doc_id` is generated
- `PDF/TXT` files are saved and indexed into Pinecone
- `CT/X-ray` images are saved locally and linked to the same `doc_id`
- Upload metadata is stored in MongoDB

### 3️⃣ Diagnosis Flow

#### 📄 For PDF/TXT reports
- Text is extracted and split into chunks
- Chunks are embedded using Gemini embeddings
- Vectors are stored in Pinecone
- When the user asks a question:
  - the query is embedded
  - relevant chunks are retrieved
  - Groq generates the final structured answer

#### 🩻 For image-only CT/X-ray uploads
- The image is loaded and encoded
- Gemini Vision receives:
  - the image
  - the user question
- The model returns:
  - probable diagnosis
  - key findings
  - suggested next steps

### 4️⃣ Doctor Flow
- Doctor searches by patient username
- Diagnosis history is fetched from MongoDB
- Doctor can review prior questions, answers, and sources

---

## 🌟 Why This Project Stands Out

- Combines **text RAG** and **vision AI** in one app
- Uses the right model for the right modality:
  - `Groq` for text report reasoning
  - `Gemini Vision` for CT/X-ray images
- Maintains a unified `doc_id` workflow across uploads and diagnosis
- Includes both patient and doctor roles for a more realistic healthcare workflow

---

## 📂 Project Structure

```text
MedicalReportDiagnosis-main/
├── assets/
├── client/
│   └── app.py
├── server/
│   ├── main.py
│   ├── auth/
│   ├── config/
│   │   └── db.py
│   ├── diagnosis/
│   │   ├── query.py
│   │   └── route.py
│   └── reports/
│       ├── route.py
│       └── vectorstore.py
├── uploaded_reports/
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd MedicalReportDiagnosis-main
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

For Linux/Mac:

```bash
python -m venv venv
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables

Create a `.env` file in the project root:

```env
MONGO_URI=
DB_NAME=rbac-diagnosis
PINECONE_API_KEY=
PINECONE_INDEX_NAME=rbac-diagnosis-index
PINECONE_ENV=us-east-1
GOOGLE_API_KEY=
GROQ_API_KEY=
UPLOAD_DIR=./uploaded_reports
API_URL=http://127.0.0.1:8000
```

---

## ▶️ Run the Project

### Start the backend

```bash
python -m uvicorn main:app --reload
```

If needed, use:

```bash
python -m uvicorn server.main:app --reload
```

### Start the frontend

Open another terminal:

```bash
python -m streamlit run client/app.py
```

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/signup` | Register a user |
| `GET` | `/auth/login` | Login user |
| `POST` | `/reports/upload` | Upload reports and optional images |
| `POST` | `/diagnosis/from_report` | Generate diagnosis |
| `GET` | `/diagnosis/by_patient_name` | View patient diagnosis history |

---

## 👤 Patient Workflow

1. Sign up or log in as a `patient`
2. Upload:
   - PDF/TXT reports, or
   - CT image, or
   - X-ray image
3. Copy the generated `doc_id`
4. Go to `Ask & Diagnose`
5. Ask a question using the `doc_id`
6. Receive the AI-generated response

---

## 👨‍⚕️ Doctor Workflow

1. Log in as a `doctor`
2. Search by patient username
3. View the patient's diagnosis history

---

## 📌 Current Limitations

- Supports only `PNG/JPG/JPEG` for image analysis
- Does not support full `DICOM` processing yet
- AI output is for demo/educational use, not real clinical use

---

## 🔮 Future Enhancements

- 🧬 DICOM support for radiology workflows
- 🔐 JWT/session-based authentication
- 📊 Better doctor analytics dashboard
- 🧾 Stronger citation of retrieved evidence
- 🖼 Multi-image case analysis

---

## ⚠️ Disclaimer

This project is built for **educational and demonstration purposes only**. It is **not a certified medical system** and should not replace professional medical advice or diagnosis.
