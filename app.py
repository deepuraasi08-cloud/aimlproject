import os
import predict_compiled as pc
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "smart_lender_secret_key_for_session"

# Category mapping
gender_map = {'male': 1, 'female': 0}
married_map = {'yes': 1, 'no': 0}
dependents_map = {'0': 0, '1': 1, '2': 2, '3+': 3}
education_map = {'graduate': 1, 'not graduate': 0}
self_employed_map = {'yes': 1, 'no': 0}
property_area_map = {'rural': 0, 'semiurban': 1, 'urban': 2}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Check if model is loaded
        try:
            # Check if input is JSON (from Fetch API) or Form Data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form

            # Extract fields
            gender = data.get('gender', 'male').lower()
            married = data.get('married', 'no').lower()
            dependents = data.get('dependents', '0').lower()
            education = data.get('education', 'graduate').lower()
            self_employed = data.get('self_employed', 'no').lower()
            property_area = data.get('property_area', 'semiurban').lower()
            
            # Numeric inputs validation and fallback
            try:
                applicant_income = float(data.get('applicantincome', 0))
                coapplicant_income = float(data.get('coapplicantincome', 0))
                loan_amount = float(data.get('loanamount', 0))
                loan_term = float(data.get('loan_amount_term', 360))
                
                # New Guideline Parameters
                credit_score = float(data.get('credit_score', 750))
                existing_emis = float(data.get('existing_emis', 0))
                
                # Convert credit score to binary credit history guidelines for model prediction
                credit_history = 1.0 if credit_score >= 750 else 0.0
            except ValueError as e:
                return jsonify({"status": "error", "message": f"Invalid numeric input: {str(e)}"}), 400

            # Encode categories
            gender_val = gender_map.get(gender, 1)
            married_val = married_map.get(married, 0)
            dependents_val = dependents_map.get(dependents, 0)
            education_val = education_map.get(education, 1)
            self_employed_val = self_employed_map.get(self_employed, 0)
            property_area_val = property_area_map.get(property_area, 1)

            # Construct feature dictionary for the compiled model prediction
            features_dict = {
                'gender': float(gender_val),
                'married': float(married_val),
                'dependents': float(dependents_val),
                'education': float(education_val),
                'self_employed': float(self_employed_val),
                'applicantincome': float(applicant_income),
                'coapplicantincome': float(coapplicant_income),
                'loanamount': float(loan_amount),
                'loan_amount_term': float(loan_term),
                'credit_history': float(credit_history),
                'property_area': float(property_area_val)
            }

            # Predict probability using compiled pure-python model (no numpy, pandas, or xgboost needed)
            prob_approved = pc.predict_probability(features_dict)
            prob_rejected = 1.0 - prob_approved

            rejection_reasons = []
            approval_reasons = []
            compensating_factors = []
            
            total_income = applicant_income + coapplicant_income
            actual_loan = loan_amount * 1000
            
            # Key Underwriting Metrics
            dti_ratio = 0.0
            if total_income > 0:
                dti_ratio = (existing_emis / total_income) * 100
                
            primary_dti = 0.0
            if applicant_income > 0:
                primary_dti = (existing_emis / applicant_income) * 100
                
            loan_to_income_ratio = 0.0
            if total_income > 0:
                # requested loan relative to monthly combined income
                loan_to_income_ratio = actual_loan / total_income
                
            disposable_income = total_income - existing_emis
            
            # Evaluate Alternative Resources (Compensating Factors)
            # Alternative 1: Co-applicant Income Cushion
            if coapplicant_income > 0 and primary_dti > 40.0 and dti_ratio <= 40.0:
                compensating_factors.append(f"Co-Applicant Cushion: Primary applicant DTI is {primary_dti:.1f}%, but co-applicant income (₹{coapplicant_income:,.2f}) cushions risk, bringing combined DTI to a safe {dti_ratio:.1f}%.")
            
            # Alternative 2: Stellar Credit Score Buffer
            if credit_score >= 780 and dti_ratio > 40.0 and dti_ratio <= 48.0:
                compensating_factors.append(f"Stellar Credit Buffer: Excellent credit score of {int(credit_score)} indicates a spotless repayment history, successfully offsetting the elevated DTI of {dti_ratio:.1f}%.")
                
            # Alternative 3: Low Loan-to-Income Exposure
            if dti_ratio > 40.0 and loan_to_income_ratio <= 18.0:
                compensating_factors.append(f"Low Exposure Multiplier: The requested loan amount (₹{actual_loan:,.2f}) represents only {loan_to_income_ratio:.1f} months of combined income, limiting total default exposure.")
                
            # Alternative 4: Ample Net Cash Flow
            if dti_ratio > 40.0 and disposable_income >= 25000:
                compensating_factors.append(f"High Net Cash Flow: Even with a DTI of {dti_ratio:.1f}%, the high combined income leaves an ample monthly cash surplus of ₹{disposable_income:,.2f} for living expenses.")

            # Decision Logic with Dynamic Policy Override
            base_decision = "Approved" if prob_approved >= 0.5 else "Rejected"
            prediction_result = base_decision
            confidence = prob_approved * 100 if prob_approved >= 0.5 else prob_rejected * 100
            
            # Policy Override: If model rejected but credit score is high (>=750), DTI is within tolerance (<=48%), and we have compensating factor(s)
            if base_decision == "Rejected" and credit_score >= 750 and dti_ratio <= 48.0 and len(compensating_factors) >= 1:
                prediction_result = "Approved"
                confidence = 65.0  # Set reasonable confidence score for override approval
                approval_reasons.append("Approved via Policy Override: High credit score and strong alternative resources successfully mitigated standard risk parameters.")

            # Generate Reasons
            if prediction_result == "Approved":
                if credit_score >= 750:
                    approval_reasons.append(f"Excellent Credit Profile: Your credit score of {int(credit_score)} demonstrates strong financial discipline and a low default risk.")
                if dti_ratio <= 30.0:
                    approval_reasons.append(f"Healthy Debt-to-Income (DTI) Ratio: Your monthly debt commitments consume only {dti_ratio:.1f}% of your income, which is well below the standard 40% risk threshold.")
                if loan_to_income_ratio <= 36.0:
                    approval_reasons.append("Comfortable Loan-to-Income Limit: The requested loan amount is within a conservative multiple of your monthly income, ensuring comfortable repayment capacity.")
                
                # Append compensating factors if any
                for factor in compensating_factors:
                    approval_reasons.append(f"Compensating Strength - {factor}")
                    
                if not approval_reasons:
                    approval_reasons.append("Strong Underwriting Profile: The applicant's aggregate profile features satisfy all risk management eligibility criteria.")
            else:
                if credit_score < 750:
                    rejection_reasons.append(f"Low Credit Score: Your score of {int(credit_score)} is below the required 750 threshold. A score of 750 or higher demonstrates strong creditworthiness.")
                if total_income <= 0:
                    rejection_reasons.append("Stable Income Missing: Total monthly income must be greater than zero to justify EMI repayments.")
                elif dti_ratio > 40.0:
                    if compensating_factors:
                        # DTI is high, but not enough compensating factors to override (e.g. score between 750-780, or DTI > 48%)
                        rejection_reasons.append(f"Elevated DTI with Insufficient Mitigants: Your DTI is {dti_ratio:.1f}%. While some alternatives exist, they do not fully offset the high debt-to-income exposure.")
                    else:
                        rejection_reasons.append(f"High Debt-to-Income (DTI) Ratio: Your existing debts of ₹{existing_emis:,.2f} take up {dti_ratio:.1f}% of your monthly income. Lenders check this ratio to ensure you aren't over-leveraged (benchmark is under 40%).")
                
                if self_employed_val == 1 and applicant_income < 3000:
                    rejection_reasons.append("High-Risk Employment Profile: Self-employed applicants with monthly incomes under ₹3,000 represent elevated default risk profiles.")
                
                if not rejection_reasons:
                    rejection_reasons.append("Risk Threshold Breached: The credit profile does not meet the minimum aggregate scoring requirements for automated approval.")

            # Store result in session
            session['prediction_result'] = prediction_result
            session['confidence'] = round(float(confidence), 1)
            session['rejection_reasons'] = rejection_reasons
            session['approval_reasons'] = approval_reasons
            session['applicant_data'] = {
                'gender': gender.capitalize(),
                'married': married.capitalize(),
                'dependents': dependents,
                'education': education.title(),
                'self_employed': self_employed.capitalize(),
                'applicantincome': applicant_income,
                'coapplicantincome': coapplicant_income,
                'loanamount': loan_amount,
                'loan_amount_term': loan_term,
                'credit_score': int(credit_score),
                'existing_emis': existing_emis,
                'dti_ratio': round(float(dti_ratio), 1) if 'dti_ratio' in locals() else (round((existing_emis / (applicant_income + coapplicant_income) * 100), 1) if (applicant_income + coapplicant_income) > 0 else 0.0),
                'credit_history': "Strong (750+)" if credit_history == 1.0 else "Weak (<750)",
                'property_area': property_area.capitalize()
            }

            if request.is_json:
                return jsonify({"status": "success", "redirect": url_for('result')})
            else:
                return redirect(url_for('result'))

        except Exception as e:
            if request.is_json:
                return jsonify({"status": "error", "message": str(e)}), 500
            else:
                return render_template('404.html', error=str(e))

    # GET request: render the form page
    return render_template('predict.html')

@app.route('/result')
def result():
    # If no prediction result in session, redirect to predict form
    if 'prediction_result' not in session:
        return redirect(url_for('predict'))
    
    result_data = {
        'prediction': session.get('prediction_result'),
        'confidence': session.get('confidence'),
        'applicant': session.get('applicant_data'),
        'rejection_reasons': session.get('rejection_reasons', []),
        'approval_reasons': session.get('approval_reasons', [])
    }
    return render_template('result.html', data=result_data)

@app.route('/about')
def about():
    # Model performance stats for rendering charts
    model_stats = {
        'Decision Tree': {'train': 82.0, 'test': 81.8},
        'Random Forest': {'train': 81.5, 'test': 83.1},
        'KNN': {'train': 81.1, 'test': 84.4},
        'XGBoost': {'train': 94.7, 'test': 81.1}
    }
    return render_template('about.html', stats=model_stats)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # Bind to PORT environment variable assigned by the cloud platform, fallback to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
