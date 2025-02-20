import streamlit as st
import pandas as pd
import plotly.express as px
from data_handler import load_data, save_data

def reports_page():
    st.title("📊 التقارير وتفصيل النقدية")

    # تحميل البيانات
    data = load_data()

    # حساب إجمالي الإيرادات (إجمالي الدخل)
    total_revenue = sum(order["final_total"] for order in data["orders"])

    # حساب إجمالي المصروفات
    total_expenses = sum(expense["amount"] for expense in data.get("expenses", []))

    # حساب إجمالي الربح الصافي (مع استبعاد الخصم الإضافي)
    total_profit = sum(
        sum(
            (item["price"] - next((p["original_price"] for p in data["products"] if p["name"] == item["name"]), 0)) * item["quantity"]
            for item in order["products"]
        ) - order.get("additional_discount", 0)  # استبعاد الخصم الإضافي
        for order in data["orders"]
    ) - total_expenses

    # حساب الرصيد النقدي (إجمالي الدخل - المصروفات)
    cash_balance = total_revenue - total_expenses

    # عرض الملخص المالي
    st.subheader("📊 الملخص المالي")
    st.write(f"💰 **إجمالي الدخل:** {total_revenue:.2f} جنيه")
    st.write(f"💸 **إجمالي المصروفات:** {total_expenses:.2f} جنيه")
    st.write(f"📈 **الربح الصافي:** {total_profit:.2f} جنيه")
    st.write(f"💵 **الرصيد النقدي:** {cash_balance:.2f} جنيه")

    # إضافة المصروفات
    st.subheader("💵 إدارة المصروفات")
    with st.form("expense_form"):
        expense_name = st.text_input("📌 اسم المصروف")
        expense_amount = st.number_input("💰 المبلغ", min_value=0.0, step=0.01, format="%.2f")
        expense_comment = st.text_area("📝 ملاحظات إضافية", placeholder="ملاحظات عن المصروف")

        submitted = st.form_submit_button("✅ إضافة المصروف")
        if submitted:
            if not expense_name:
                st.error("⚠️ يجب إدخال اسم المصروف!")
            else:
                new_expense = {
                    "name": expense_name,
                    "amount": expense_amount,
                    "comment": expense_comment
                }
                data.setdefault("expenses", []).append(new_expense)
                save_data(data)
                st.success("✅ تم إضافة المصروف بنجاح!")
                st.rerun()

    # عرض المصروفات مع خيار الحذف
    if "expenses" in data and data["expenses"]:
        st.subheader("📜 قائمة المصروفات")
        for idx, exp in enumerate(data["expenses"]):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📌 **{exp['name']}** - 💰 {exp['amount']:.2f} جنيه")
                if exp["comment"]:
                    st.write(f"📝 {exp['comment']}")
            with col2:
                if st.button("🗑️ حذف", key=f"del_exp_{idx}"):
                    data["expenses"].remove(exp)
                    save_data(data)
                    st.success("🗑️ تم حذف المصروف!")
                    st.rerun()

    # قسم الرسوم البيانية
    st.subheader("📊 الرسوم البيانية")

    # رسم الإيرادات اليومية (بالإنجليزية)
    if data["orders"]:
        df_sales = pd.DataFrame([
            {"Date": order["timestamp"][:10], "Revenue": order["final_total"]}
            for order in data["orders"]
        ])
        df_sales = df_sales.groupby("Date").sum().reset_index()

        fig = px.line(df_sales, x="Date", y="Revenue", title="📈 Daily Revenue", markers=True)
        fig.update_traces(line=dict(color="blue"))
        fig.update_layout(xaxis_title="Date", yaxis_title="Revenue (EGP)")
        st.plotly_chart(fig, use_container_width=True)

    # المنتجات الأكثر مبيعًا (بالإنجليزية)
    st.subheader("🏆 المنتجات الأكثر مبيعًا")
    product_sales = {}
    for order in data["orders"]:
        for item in order["products"]:
            product_sales[item["name"]] = product_sales.get(item["name"], 0) + item["quantity"]

    if product_sales:
        df_products = pd.DataFrame(list(product_sales.items()), columns=["Product", "Sold"])
        df_products = df_products.sort_values(by="Sold", ascending=False)

        fig = px.bar(df_products[:5], x="Product", y="Sold", title="🏆 Top Selling Products", text_auto=True)
        fig.update_traces(marker_color="green")
        fig.update_layout(xaxis_title="Product", yaxis_title="Units Sold")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    reports_page()
