# Smart Lender – AI-Powered Loan Approval Prediction System

Smart Lender is a machine learning-powered web application designed to predict the creditworthiness of loan applicants, enabling banks and financial institutions to make faster, data-driven loan approval decisions. The platform leverages classification algorithms (Decision Tree, Random Forest, K-Nearest Neighbors, and XGBoost) to evaluate applicant data and determine the likelihood of loan repayment or default.

The application processes structured applicant inputs such as gender, marital status, education, employment status, income, loan amount, loan term, credit history, and property area. After training and evaluating all four models, the best-performing model (XGBoost at 94.7% training accuracy and 81.1% testing accuracy) is saved and integrated into a Flask web application for real-time prediction.

Designed with a premium banking-style user interface, Smart Lender features custom animations, full mobile responsiveness, glassmorphic layout cards, interactive Chart.js visualizations, and an IBM Cloud-ready deployment architecture.

---

## Folder Structure

```
Smart-Lender/
├── app.py                  # Main Flask Web Server & API Backend
├── model.pkl               # Serialized Best XGBoost Model
├── requirements.txt        # Python Dependancy List
├── README.md               # Project Documentation
├── train_model.py          # Machine Learning training pipeline
├── dataset/
│   └── loan.csv            # Applicant profile training dataset
├── static/
│   ├── css/
│   │   └── style.css       # Custom premium banking stylesheet
│   └── js/
│       └── script.js       # Client side interactive logic and validations
└── templates/
    ├── base.html           # Shared layout layout template
    ├── index.html          # Portal home page & hero section
    ├── predict.html        # Multi-section loan application form
    ├── result.html         # Score metric and dynamic evaluation outcomes
    ├── about.html          # Platform specifications and ML analytics charts
    ├── contact.html        # Contact forms and map placement holders
    └── 404.html            # Custom page not found visual
```

---

## Machine Learning Pipeline & Model Scores

Four classification algorithms are trained in the pipeline:
1. **Decision Tree Classifier** (Train: 82.0%, Test: 81.8%)
2. **Random Forest Classifier** (Train: 81.5%, Test: 83.1%)
3. **K-Nearest Neighbors (KNN)** (Train: 81.1%, Test: 84.4%)
4. **XGBoost Classifier** (Train: 94.7%, Test: 81.1%)

The **XGBoost Classifier** is chosen as the production model due to its high capacity for modeling complex multi-feature relationships and its robust real-time scoring capabilities.

---

## How to Set Up and Run

### Prerequisites
Make sure you have Python 3.8+ installed on your system.

### 1. Clone the repository and navigate to the project directory:
```bash
cd sl
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```
*(Or use `uv pip install -r requirements.txt` for extremely fast installations)*

### 3. Run model training:
Ensure the raw training dataset is located in `dataset/loan.csv`, then execute the training script:
```bash
python train_model.py
```
This will train the classifiers, log performance scores, and export the trained model to `model.pkl`.

### 4. Start the Flask application:
```bash
python app.py
```
By default, the application will run locally at `http://127.0.0.1:5000/`.

---

## Scope of Deployment
* **IBM Cloud Deployment**: Designed for containerization (Docker) and deployment using Cloud Foundry or containerized environments (Kubernetes/RedHat OpenShift) on IBM Cloud.
* **Banking Operations**: Perfect for commercial banks, credit unions, and microfinance networks to assess applicant risk profiles instantly.
