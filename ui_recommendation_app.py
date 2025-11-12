import streamlit as st
import pandas as pd
import joblib

# ============================================================
# CONFIG
# ============================================================
MODEL_PATH = "streaming/recommendation_model.pkl"
st.set_page_config(page_title="E-Commerce Recommendation Predictor", layout="wide")

# ============================================================
# LOAD MODEL
# ============================================================
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

st.title("🛍️ E-Commerce Purchase Likelihood Predictor")
st.caption("Predicts customer purchase percentage for given product attributes.")
st.markdown("---")

# ============================================================
# SINGLE RECORD PREDICTION
# ============================================================
st.header("Single Prediction")

col1, col2 = st.columns(2)

with col1:
    num_clicks = st.number_input("Number of Clicks", 0, 1000, 200)
    rating = st.number_input("Product Rating", 0.0, 5.0, 4.3)
    discount = st.slider("Discount Percentage", 0, 100, 20)

with col2:
    purchases_last_30 = st.number_input("Purchases in Last 30 Days", 0, 500, 60)
    category = st.selectbox("Category", ["Electronics", "Clothing", "Home", "Beauty", "Books"])
    price = st.number_input("Product Price (₹)", 50.0, 10000.0, 2500.0)

if st.button("Predict for Single Input"):
    input_data = pd.DataFrame([{
        "num_clicks": num_clicks,
        "rating": rating,
        "discount_percentage": discount,
        "purchases_last_30_days": purchases_last_30,
        "category": category,
        "price": price
    }])
    pred = model.predict(input_data)[0]
    st.success(f"Predicted Purchase Likelihood: {pred:.2f}%")

# ============================================================
# MULTIPLE RECORDS (FILE UPLOAD) PREDICTION 
# ============================================================
st.markdown("---")
st.header("Batch Prediction from File")

uploaded_pred_file = st.file_uploader(
    "Upload CSV file for prediction (without target column)",
    type="csv"
)

if uploaded_pred_file:
    df_new = pd.read_csv(uploaded_pred_file)
    st.write("**Preview of Uploaded Data:**")
    st.dataframe(df_new.head())

    if st.button("Predict for Uploaded File"):
        preds = model.predict(df_new)
        df_new["predicted_purchase_percent"] = preds

        # Sort to get Top 5 recommendations
        df_sorted = df_new.sort_values(by="predicted_purchase_percent", ascending=False)
        top5 = df_sorted.head(5)

        st.success(f"Predictions generated for {len(df_new)} records.")
        st.subheader("Top 5 Recommended Products (Highest Purchase Likelihood)")
        st.dataframe(top5.style.highlight_max(subset=["predicted_purchase_percent"], color="lightgreen"))

        # Option to download full prediction results
        csv_output = df_new.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download All Predictions as CSV",
            data=csv_output,
            file_name="predicted_output.csv",
            mime="text/csv"
        )

# ============================================================
# RETRAIN SECTION         
# ============================================================
st.markdown("---")
st.header("Retrain Model with New Labeled Data")

uploaded_train_file = st.file_uploader(
    "Upload CSV with 'purchase_percent' column for retraining",
    type="csv",
    key="train_file"
)

if uploaded_train_file:
    df_train = pd.read_csv(uploaded_train_file)
    st.write("**Preview of Training Data:**")
    st.dataframe(df_train.head())

    if "purchase_percent" not in df_train.columns:
        st.error("CSV must include 'purchase_percent' column.")
    else:
        if st.button("Retrain Model"):
            X_new = df_train.drop(columns=["purchase_percent"])
            y_new = df_train["purchase_percent"]

            with st.spinner("Retraining in progress..."):
                model.fit(X_new, y_new)
                joblib.dump(model, MODEL_PATH)
            st.success("✅ Model retrained and saved successfully.")
