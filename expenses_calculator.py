import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cultural Event Expense Tracker", layout="centered")

st.title("🧾 Cultural Insights Expense Tracker")

# Initialize session state
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(columns=["Item", "Category", "Amount (₹)"])

st.subheader("➕ Add a New Expense")

# Input form
with st.form(key="expense_form", clear_on_submit=True):
    item = st.text_input("Item / Description")
    category = st.selectbox("Category", ["Food", "Travel", "Accommodation", "Miscellaneous"])
    amount = st.number_input("Enter amount in ₹", min_value=0.0, step=10.0, format="%.2f")
    submit = st.form_submit_button("Add Expense")

# Add expense
if submit:
    if item and amount:
        new_expense = {"Item": item, "Category": category, "Amount (₹)": amount}
        new_df = pd.DataFrame([new_expense])
        st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_df], ignore_index=True)
        st.success(f"Added expense: {item} – ₹{amount:.2f}")
    else:
        st.warning("Please fill out both the item and amount.")

# Display table
st.subheader("📋 Expense Log")
if not st.session_state["expenses"].empty:
    st.dataframe(st.session_state["expenses"], use_container_width=True)
    total = st.session_state["expenses"]["Amount (₹)"].sum()
    st.markdown(f"### 💰 Total Spent: ₹{total:.2f}")
else:
    st.info("No expenses added yet.")

# Optional: Reset
if st.button("🔄 Clear All Expenses"):
    st.session_state["expenses"] = pd.DataFrame(columns=["Item", "Category", "Amount (₹)"])
    st.success("All expenses cleared.")
