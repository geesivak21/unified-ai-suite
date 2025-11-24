# 🧠 AI Utility Suite

A combined **Streamlit application** that integrates three powerful AI utilities in one place:

1. **📄 RFP Summarizer** – Summarize large RFP or PDF documents using OpenAI.
2. **🧾 Azure Document OCR** – Extract and structure information from documents using Azure Document Intelligence + Azure OpenAI.
3. **💬 Smart Q&A Assistant** – Ask questions about databases or text using natural language or voice.

---

## 🏗️ Project Structure

```

combined_app/
│
├── main.py                # Unified Streamlit launcher
├── config.py              # Loads all API keys from .env
├── .env                   # Shared environment variables
│
├── Extraction/            # Azure OCR application
│   ├── azure_doc_ocr.py
│   ├── preprocess.py
│   ├── config.py (optional local settings)
│
├── Summarization/         # RFP Summarizer application
│   ├── rfp_summarizer.py
│
└── DBRag/                 # Smart Q&A Assistant application
├── smart_qa_assistant.py

````

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd combined_app
````

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv combappvenv
combappvenv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the Application

From the root folder:

```bash
streamlit run main.py
```

Then open your browser at:
👉 [http://localhost:8501](http://localhost:8501)

Use the **sidebar navigation** to switch between:

* 📄 RFP Summarizer
* 🧾 Azure Document OCR
* 💬 Smart Q&A Assistant

---

## 🧠 Tech Stack

* [Streamlit](https://streamlit.io/) – UI framework
* [OpenAI API](https://platform.openai.com/docs) – For summarization and Q&A
* [Azure AI Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
* [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/) – For OCR-based LLM extraction
* [Python-dotenv](https://pypi.org/project/python-dotenv/) – For environment management

---

### 👨‍💻 Author

**G. Siva Kumar**
📧 [gesivak21@gmail.com](mailto:gesivak21@gmail.com)
🌐 [GitHub](https://github.com/gesivak21/Portfolio)

