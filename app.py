import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file, flash, redirect, url_for
import pickle
from pymongo import MongoClient
import numpy as np
from fpdf import FPDF
import os
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["employee_db"]
collection = db["employees"]

# Load the trained model and metadata
with open('model_metadata.pkl', 'rb') as f:
    metadata = pickle.load(f)

model = metadata['model']
model_accuracy = metadata['accuracy']
feature_names = metadata['feature_names']

# Define the input features
FEATURES = ['Age', 'BusinessTravel', 'DailyRate', 'DistanceFromHome', 'Education',
            'Department', 'YearsAtCompany', 'WorkLifeBalance', 'YearsSinceLastPromotion']

@app.route('/')
def home():
    return render_template('index.html', model_accuracy=model_accuracy)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        employee_id = request.form.get("EmployeeID")
        name = request.form.get("Name")
        inputs = {feature: request.form.get(feature) for feature in FEATURES}

        # Convert inputs to DataFrame
        df = pd.DataFrame([inputs])

        numeric_features = ['Age', 'DailyRate', 'DistanceFromHome', 'Education',
                          'YearsAtCompany', 'WorkLifeBalance', 'YearsSinceLastPromotion']
        for feature in numeric_features:
            df[feature] = df[feature].astype(int)

        # One-hot encode categorical features
        df = pd.get_dummies(df, columns=['BusinessTravel', 'Department'], drop_first=True)

        # Align DataFrame with model features
        for col in feature_names:
            if col not in df.columns:
                df[col] = 0
        df = df[feature_names]

        # Prediction
        prediction = model.predict(df)
        output = 'Employee Might Leave The Job' if prediction[0] == 1 else 'Employee Might Not Leave The Job'

        # Dynamic Suggestions
        suggestions = generate_suggestions(prediction[0], inputs)

        # Save to MongoDB
        collection.insert_one({
            "EmployeeID": employee_id,
            "Name": name,
            **inputs,
            "Prediction": output,
            "Suggestions": suggestions
        })

        return render_template(
            'index.html',
            prediction_text=output,
            model_accuracy=model_accuracy,
            suggestions=suggestions
        )
    except Exception as e:
        app.logger.error(f"Error in predict route: {str(e)}")
        flash("An error occurred during prediction. Please try again.", "error")
        return redirect(url_for('home'))

@app.route("/view_previous_prediction", methods=["GET", "POST"])
def view_previous_prediction():
    if request.method == "POST":
        employee_id = request.form.get("EmployeeID")
        prediction = collection.find_one({"EmployeeID": str(employee_id)})

        if prediction:
            formatted_prediction = {
                "EmployeeID": prediction.get("EmployeeID"),
                "Name": prediction.get("Name"),
                "Prediction": prediction.get("Prediction"),
                "Suggestions": prediction.get("Suggestions", []),
            }
            return render_template("view_previous_prediction.html", prediction=formatted_prediction)
        else:
            error_message = f"No prediction found for Employee ID: {employee_id}"
            return render_template("view_previous_prediction.html", error=error_message)
    return render_template("view_previous_prediction.html")
@app.route("/download_report/<employee_id>")
def download_report(employee_id):
    try:
        prediction = collection.find_one({"EmployeeID": employee_id})
        
        if not prediction:
            flash("No prediction found for this employee ID", "error")
            return redirect(url_for('view_previous_prediction'))

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Simple content to test
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Employee Retention Report", ln=1, align='C')
        pdf.cell(200, 10, txt=f"Employee ID: {employee_id}", ln=1)
        pdf.cell(200, 10, txt=f"Name: {prediction.get('Name', 'N/A')}", ln=1)
        pdf.cell(200, 10, txt=f"Prediction: {prediction.get('Prediction', 'N/A')}", ln=1)
        
        # Save to a temporary file
        temp_file = f"temp_report_{employee_id}.pdf"
        pdf.output(temp_file)
        
        # Send the file
        response = send_file(
            temp_file,
            as_attachment=True,
            download_name=f"employee_report_{employee_id}.pdf"
        )
        
        # Schedule the file for deletion after sending
        @response.call_on_close
        def remove_file():
            try:
                os.remove(temp_file)
            except:
                pass
                
        return response
        
    except Exception as e:
        app.logger.error(f"PDF error: {str(e)}")
        flash("Failed to generate report", "error")
        return redirect(url_for('view_previous_prediction'))

@app.route('/work_life_calculator', methods=['GET'])
def work_life_calculator():
    return render_template('work_life_calculator.html')

@app.route('/calculate_wlb', methods=['POST'])
def calculate_wlb():
    try:
        work_hours = int(request.form['WorkHours'])
        commute_time = int(request.form['CommuteTime'])
        holidays = int(request.form['Holidays'])
        leisure_hours = int(request.form['LeisureHours'])
        dependents = int(request.form['Dependents'])

        if work_hours > 50 or commute_time > 90 or holidays < 10 or leisure_hours < 1:
            work_life_rating = "Bad"
        elif work_hours <= 40 and commute_time <= 30 and holidays >= 25 and leisure_hours >= 2 and dependents <= 2:
            work_life_rating = "Best"
        elif work_hours <= 45 and commute_time <= 60 and holidays >= 15 and dependents <= 3:
            work_life_rating = "Better"
        else:
            work_life_rating = "Good"

        return render_template('work_life_calculator.html', work_life_rating=work_life_rating)
    except Exception as e:
        flash("Invalid input values. Please check your entries.", "error")
        return redirect(url_for('work_life_calculator'))

@app.route('/view_all_predictions')
def view_all_predictions():
    try:
        predictions = list(collection.find())
        return render_template('view_all_predictions.html', predictions=predictions)
    except Exception as e:
        app.logger.error(f"Error fetching predictions: {str(e)}")
        flash("Failed to load predictions. Please try again.", "error")
        return redirect(url_for('home'))
    

def generate_suggestions(prediction, inputs):
    suggestions = []
    age = int(inputs.get('Age', 0))
    years_at_company = int(inputs.get('YearsAtCompany', 0))
    years_since_promotion = int(inputs.get('YearsSinceLastPromotion', 0))
    work_life_balance = int(inputs.get('WorkLifeBalance', 0))
    business_travel = inputs.get('BusinessTravel')
    department = inputs.get('Department')
    distance_from_home = int(inputs.get('DistanceFromHome', 0))
    education = int(inputs.get('Education', 0))
    daily_rate = int(inputs.get('DailyRate', 0))
    education_levels = {1: "BSc", 2: "BTech", 3: "MSc", 4: "PhD"}
    wlb_levels = {1: "Bad", 2: "Good", 3: "Better", 4: "Best"}

    # Base suggestions for all employees
    base_suggestions = [
        "Conduct regular one-on-one meetings to understand employee concerns",
        "Provide clear career progression paths",
        "Offer competitive compensation and benefits packages"
    ]
    suggestions.extend(base_suggestions)

    if prediction == 1:  # High attrition risk
        suggestions.append("🚨 High Priority: Immediate retention intervention needed for this employee.")

        # Promotion-related suggestions
        if years_since_promotion >= 3:
            suggestions.append(f"🔝 Critical: Employee hasn't been promoted in {years_since_promotion} years. Consider: "
                             f"{'Promotion' if years_at_company > 3 else 'Career development plan'} "
                             f"and leadership training")
        elif years_since_promotion >= 2:
            suggestions.append("📈 Employee may be ready for advancement. Options: "
                            "Lateral move to gain new skills or special project assignment")

        # Work-life balance improvements
        if work_life_balance <= 2:
            suggestions.append(f"⚖️ Work-life balance is {wlb_levels.get(work_life_balance, 'suboptimal')}. Recommend: "
                             f"{'Flexible hours' if distance_from_home > 10 else 'Hybrid work options'}, "
                             f"mental health days, and workload review")
            if work_life_balance == 1:
                suggestions.append("🆘 Urgent: Mandatory time off and workload reduction required immediately")

        # Department-specific strategies
        dept_strategies = {
            "Sales": [
                f"💰 Sales-specific: Consider {'commission structure review' if daily_rate < 800 else 'performance bonuses'}",
                "Implement peer recognition program",
                "Provide advanced sales training"
            ],
            "HR": [
                "👥 HR-specific: Leadership development program",
                "Professional certification sponsorship",
                "Employee engagement initiative leadership role"
            ],
            "Research & Development": [
                "🔬 R&D-specific: Assign to innovation task force",
                "Conference attendance budget",
                "Patent incentive program"
            ]
        }
        suggestions.extend(dept_strategies.get(department, []))

        # Travel-related suggestions
        if business_travel == "Travel_Frequently":
            travel_suggestions = [
                "✈️ Frequent traveler support:",
                "- Premium travel accommodations",
                "- Mandatory recovery days post-travel",
                f"- {'Remote work options' if distance_from_home > 20 else 'Travel reduction'} program"
            ]
            suggestions.extend(travel_suggestions)

        # Age-based strategies
        if age < 30:
            suggestions.extend([
                "👶 Younger employee strategies:",
                "- Mentorship program pairing",
                "- Skills development budget",
                "- Fast-track leadership program"
            ])
        elif age > 45:
            suggestions.extend([
                "🧓 Experienced employee strategies:",
                "- Knowledge transfer initiatives",
                "- Recognition for institutional knowledge",
                "- Flexible retirement options"
            ])

        # Education-level strategies
        if education >= 3:
            suggestions.append(f"🎓 Advanced degree ({education_levels.get(education)}) holder: "
                             "Assign complex projects and research opportunities")

    else:  # Low attrition risk
        suggestions.append("✅ Employee shows good engagement. Focus on retention maintenance:")

        # Retention reinforcement
        if years_at_company >= 5:
            suggestions.append(f"🏅 Long-service (5+ years): Consider anniversary recognition and sabbatical options")

        # Continuous improvement
        if work_life_balance < 4:
            suggestions.append(f"⚖️ Work-life balance is {wlb_levels.get(work_life_balance)}. "
                             "Could be improved with team-building activities")

        # Proactive development
        development_suggestions = [
            "📚 Continuous learning opportunities",
            "🌱 Cross-departmental project assignments",
            "👥 Leadership shadowing program"
        ]
        suggestions.extend(development_suggestions)

        # Compensation review
        if (department == "Sales" and daily_rate < 1000) or (education >= 2 and daily_rate < 1200):
            suggestions.append("💵 Proactive compensation review recommended to maintain competitiveness")

    return suggestions[:10]

if __name__ == "__main__":
    app.run(debug=True)