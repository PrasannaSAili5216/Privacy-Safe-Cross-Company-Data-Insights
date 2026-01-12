|Home Page|
<img width="1918" height="860" alt="Home " src="https://github.com/user-attachments/assets/a93e5343-23e0-4c4d-9d7c-32f929bc6bc5" />

|Deploy Page|
<img width="1918" height="865" alt="deploy page" src="https://github.com/user-attachments/assets/4c5cb817-3890-4fc9-9448-90a446464292" />


# 🔒 Privacy-Safe Cross-Company Data Insights

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Status](https://img.shields.io/badge/Status-Prototype-green)

A privacy-preserving collaboration platform that allows competing organizations (e.g., Banks and Insurers) to gain joint insights without sharing raw data. 

**Use Case:** Financial Fraud Detection (AI for Good)

## 🚀 Key Features

- **Simulated Data Clean Room**: Compute intersections on hashed identifiers.
- **Differential Privacy**: Adds Laplace noise to aggregate counts to prevent re-identification.
- **Cortex AI Analyst (Simulated)**: Natural language interface for querying insights.
- **Role-Based Views**: Separate data views for "Global Bank" and "SafeGuard Insurance".

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Privacy Logic**: Python (NumPy, Pandas)
- **Testing**: Pytest

## 📦 Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   py -m pip install -r requirements.txt
   ```

## 🏃‍♂️ Running the App

Start the dashboard:
```bash
py -m streamlit run src/app.py
```

## 🧪 Testing

Run unit tests to verify privacy guarantees and fraud logic:
```bash
py -m pytest
```

## 📚 Project Structure

- `src/app.py`: Main dashboard application.
- `src/data_gen.py`: Generates synthetic fraud data.
- `src/fraud_analysis.py`: Implements Privacy Set Intersection (PSI) and noise.
- `src/privacy.py`: Core differential privacy functions.
- `tests/`: Unit and smoke tests.
