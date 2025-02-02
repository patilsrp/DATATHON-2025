from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
import xgboost as xgb
import torch
import numpy as np

app = Flask(__name__)

# Load dataset
df = pd.read_csv("C:\\Users\\hghar\\Downloads\\DATATHON-2025-main\\DATATHON-2025-main\\UserEngagementMetrics.csv")

# Ensure email and password formatting is consistent
df['email_id'] = df['email_id'].str.strip().str.lower()
df['password'] = df['password'].str.strip()

# Load pre-trained XGBoost model
xgb_churn_model = joblib.load('xgb_churn_model.pkl')

# Load pre-trained sentiment analysis model
sentiment_model = joblib.load('model.pkl')
sentiment_tokenizer = joblib.load('tokenizer.pkl')

# Define exact features used in churn model training
MODEL_FEATURES = [
    'Subscription Plan', 'Course Completion Rate', 'Survey Response (1-5)',
    'Time Spent per Session (mins)', 'Assignment Submission Rate', 
    'Video Watch Completion Rate', 'Engagement Score'
]

# Fixed encoding for Subscription Plan (must match training data)
SUBSCRIPTION_PLAN_MAPPING = {'basic': 0, 'premium': 1, 'enterprise': 2}

def predict_churn(user_features):
    try:
        # Convert dictionary to DataFrame
        user_features_df = pd.DataFrame([user_features])

        # Debug: Print extracted user features before encoding
        print(f"\n[DEBUG] Raw Features Before Encoding:\n{user_features_df}")

        # Encode 'Subscription Plan' correctly
        if 'Subscription Plan' in user_features_df.columns:
          plan = str(user_features_df['Subscription Plan']).lower()
          print(f"\n[DEBUG] Subscription Plan Before Encoding: {plan}")
          user_features_df['Subscription Plan'] = SUBSCRIPTION_PLAN_MAPPING.get(plan, 0)

        # Convert all numerical features to float for XGBoost compatibility
        user_features_df = user_features_df.astype('float64')

        # Debug: Print transformed user features
        print(f"\n[DEBUG] Processed Features Before Model Input:\n{user_features_df}")

        # Ensure feature order matches the training model
        user_features_df = user_features_df[MODEL_FEATURES]

        # Perform churn prediction *with probability output*
        churn_proba = xgb_churn_model.predict_proba(user_features_df)
        churn_probability = churn_proba[0][1]  # Probability of churn (value between 0 and 1)

        # Convert probability into percentage (0-100%)
        churn_rate = churn_probability * 100  

        print(f"\n[DEBUG] Churn Probability: {churn_probability:.4f}, Churn Rate: {churn_rate:.2f}%")

        return round(churn_rate, 2)

    except Exception as e:
        print(f"[ERROR] Churn Prediction Error: {e}")
        return "Churn prediction failed"


def analyze_sentiment(text):
    try:
        if not text or pd.isna(text):
            return "No feedback provided"
        inputs = sentiment_tokenizer(text, padding="max_length", truncation=True, max_length=128, return_tensors="pt")
        with torch.no_grad():
            outputs = sentiment_model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=-1).item()
        sentiment_labels = {0: "Negative", 1: "Neutral", 2: "Positive"}
        return sentiment_labels.get(prediction, "Unknown")
    except Exception as e:
        print(f"[ERROR] Sentiment Analysis Error: {e}")
        return "Sentiment analysis failed"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        email = data.get("email_id", "").strip().lower()
        password = data.get("password", "").strip()

        # Debug: Print received input
        print(f"\n[DEBUG] Received Email: {email}, Password: {password}")

        # Validate user credentials
        user_data = df[(df['email_id'] == email) & (df['password'] == password)]

        # Debug: Check if the user exists
        if user_data.empty:
            print("[ERROR] Invalid credentials.")
            return jsonify({'error': 'Invalid email or password'}), 401

        # Fetch user data
        user_data = user_data.iloc[0]

        # Print user details to confirm correct extraction
        print(f"\n[DEBUG] Extracted User Data:\n{user_data}")

        # Extract only the required features for churn prediction
        user_features = {feature: user_data.get(feature, 0) for feature in MODEL_FEATURES}

        # Debug: Check extracted features before prediction
        print(f"\n[DEBUG] Extracted Features for Prediction:\n{user_features}")

        # Predict churn rate
        churn_rate = predict_churn(user_features)

        # Perform sentiment analysis (if feedback exists)
        feedback_text = user_data.get('Feedback Sentiment', "")
        sentiment = analyze_sentiment(feedback_text)

        print(f"\n[DEBUG] Predicted Churn Rate: {churn_rate}")
        print(f"\n[DEBUG] Predicted Sentiment: {sentiment}")

        return jsonify({'churn_rate': float(churn_rate), 'sentiment': sentiment})

    except Exception as e:
        print(f"[ERROR] API Error: {e}")
        return jsonify({'error': 'An error occurred while processing the request'}), 500

if __name__ == '__main__':
    app.run(debug=True)