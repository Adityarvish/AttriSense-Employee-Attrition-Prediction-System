# AttriSense-Employee-Attrition-Prediction-System

AttriSense is a machine learning–based web application designed to help HR teams predict employee attrition and take proactive retention measures. The system uses historical employee data and an XGBoost model to predict whether an employee is likely to leave the organization.

This project was developed as a Final Year Engineering Project for my Bachelor of Engineering (Information Technology) program.

---

##  Features

- Predicts employee attrition using machine learning
- User-friendly Flask-based web interface
- Uses XGBoost for high prediction accuracy
- Stores employee data and predictions in MongoDB
- Generates personalized retention suggestions
- Work-life balance score calculation
- PDF report generation for HR analysis
- Secure employee identification using Employee ID

---

##  Machine Learning Model

- **Algorithm Used:** XGBoost Classifier  
- **Problem Type:** Binary Classification (Attrition: Yes / No)
- **Dataset:** Employee Attrition Dataset
- **Target Variable:** Attrition

## Key Features Used
- Age  
- Business Travel Frequency  
- Daily Rate  
- Distance From Home  
- Education Level  
- Department  
- Years at Company  
- Years Since Last Promotion  
- Work-Life Balance  

---

##  System Architecture

1. HR user enters employee details via web form  
2. Data is processed and passed to the trained ML model  
3. Model predicts attrition risk  
4. Results are stored in MongoDB  
5. System generates insights, suggestions, and PDF reports  

---

##  Tech Stack

- **Frontend:** HTML, CSS, Bootstrap  
- **Backend:** Python, Flask  
- **Machine Learning:** XGBoost, Scikit-learn  
- **Database:** MongoDB  
- **Other Libraries:** Pandas, NumPy, Matplotlib 
A machine learning–based web application that predicts employee attrition using XGBoost, Flask, and MongoDB to help HR teams take proactive retention decisions.
