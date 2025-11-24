# 🏭 Procurement AI Dashboard

**AI-powered procurement analytics for multi-plant manufacturing operations**

This interactive Streamlit dashboard helps procurement teams analyze vendor pricing, detect naming inconsistencies, compare material costs across plants, and chat with a SQL-powered AI procurement assistant — all enriched by Azure OpenAI.

---

# 🚀 Key Capabilities

| Feature                                        | Description                                                                                                                        |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 💰 **Cheapest Vendor Finder**                  | Identifies the lowest-price vendor per material and plant, handling zero-price anomalies intelligently.                            |
| 🧩 **Short Text Similarity Checker**           | Detects inconsistent naming, typos, and near-duplicates in material descriptions using RapidFuzz + AI logic.                       |
| 📦 **Material Price Comparison Across Plants** | Analyzes prices for the **same material across multiple plants**, showing cross-plant differences.                                 |
| 💬 **Procurement Chatbot (SQL Agent)**         | Ask procurement questions in English or via voice; the agent generates SQL queries automatically and answers with data + insights. |
| 🎙️ **Voice-to-Text Procurement Q&A**          | Use your microphone to ask procurement questions — powered by Azure OpenAI transcription.                                          |

---

# 🧠 AI Integration Summary

The app uses **Azure OpenAI** for:

### ✔️ Business Insights

Summaries of price patterns, vendor competitiveness, anomalies, and negotiation guidance.

### ✔️ ChatBot

Interprets user questions, retrieves data from the database, and delivers clear business-friendly explanations.

### ✔️ Audio Transcription

Converts spoken questions into text enabling hands-free interaction with the chatbot.

---

# 🗂️ Project Structure

```
project_root/
│
├── app.py                      # Main Streamlit application
├── config.py                   # Securely loads Azure OpenAI keys (Streamlit Secrets + .env fallback)
├── transcript.py               # Audio→text transcription logic
├── procurement.db              # SQLite database for SQL agent
├── datasets/                   # Plant-level Excel files for analysis
│   ├── Plant_1300.xlsx
│   ├── Plant_1500.xlsx
│   └── ...
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone the repository

```bash
git clone https://github.com/your-org/procurement-ai-dashboard.git
cd procurement-ai-dashboard
```

---

## 2️⃣ Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

---

## 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```
---

# 🧾 Dataset Requirements

Place all Excel files in the folder:

```
datasets/
```

Each file must follow the naming pattern:

```
Plant_XXXX.xlsx   (example: Plant_1300.xlsx)
```

### Required Columns

| Column                     | Description                                             |
| -------------------------- | ------------------------------------------------------- |
| Plant                      | Plant number (optional—filled automatically if missing) |
| Material                   | Material code                                           |
| Short Text                 | Description for similarity analysis                     |
| Supplier/Supplying Plant   | Vendor name                                             |
| Net Price                  | Unit price                                              |
| Currency                   | Price currency                                          |
| Quantity in SKU (optional) | For additional analytics                                |

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

Then open the displayed URL (usually):

```
http://localhost:8501
```

---

# 📌 Feature Breakdown

## 💰 **Task 1 — Cheapest Vendor Finder**

* Intelligent zero-price filtering
* Summary statistics (min, max, avg price)
* Vendor comparison expanders
* **AI-generated insights** per plant
* Exportable tables

---

## 🧩 **Task 2 — Short Text Similarity Checker**

Detect inconsistent or duplicate descriptions within each plant.

Includes:

* Fuzzy-matching with RapidFuzz
* Vendor → price mapping for each material
* Symmetric pair removal (A-B shown only once)
* Excel export with flagged results

---

## 📦 **Task 3 — Material Price Comparison Across Plants**

Compare the same material between plants:

* Vendor-by-vendor pricing
* Avg / min / max prices
* Expanders per material
* Export full report as Excel

---

## 💬 **Task 4 — Procurement Chatbot (SQL Agent)**

Ask questions like:

> “Which supplier provides the lowest average price for Material 1001?”
> “Show the top 10 materials with highest price variance.”
> “What is the cheapest vendor per plant?”

Includes:

* Natural-language → SQL conversion
* Automatic result summarization
* Voice-based question input

### 🎙️ Voice Input Workflow

1. Record question
2. Whisper model transcribes
3. SQL agent answers with data + insights

---

# 👨‍💼 Author

[![GitHub: gesivak21](https://img.shields.io/badge/GitHub-gesivak21-black?logo=github)](https://github.com/gesivak21)
[![Email](https://img.shields.io/badge/Email-gesivak21%40gmail.com-blue?logo=gmail)](mailto:gesivak21@gmail.com)
