import streamlit as st
import datetime
from data_handler import load_data, save_data

def orders_page():
    st.title("🛒 إنشاء طلب جديد")

    # تحميل البيانات
    data = load_data()

    # إدخال بيانات العميل
    client_name = st.text_input("👤 اسم العميل (اختياري)")
    client_phone = st.text_input("📞 رقم الهاتف (اختياري)")

    # 🔍 **اختيار المنتج من قائمة منسدلة**
    st.subheader("📦 اختر منتجًا")
    
    product_options = {product["name"]: product for product in data["products"]}
    selected_product_name = st.selectbox("📦 المنتج", ["اختر منتجًا"] + list(product_options.keys()))

    selected_products = []

    if selected_product_name != "اختر منتجًا":
        selected_product = product_options[selected_product_name]

        # يبدأ تلقائيًا بـ 1 عند اختيار المنتج
        quantity = st.number_input(
            f"🔢 الكمية من {selected_product['name']} (متوفر: {selected_product['stock']})",
            min_value=1, max_value=selected_product["stock"], step=1, value=1
        )

        selected_products.append({
            "name": selected_product["name"],
            "price": selected_product["final_price"],
            "quantity": quantity
        })

    # تطبيق الخصم الإضافي
    additional_discount = st.number_input("💵 خصم إضافي", min_value=0.0, step=0.01, format="%.2f")

    # حساب إجمالي المبلغ
    total_cost = sum(item["price"] * item["quantity"] for item in selected_products)
    final_total = max(0, total_cost - additional_discount)

    st.write(f"💰 **إجمالي السعر:** {total_cost:.2f} جنيه")
    st.write(f"📉 **بعد الخصم الإضافي:** {final_total:.2f} جنيه")

    # زر تأكيد الطلب
    if st.button("✅ تأكيد الطلب"):
        if not selected_products:
            st.error("⚠️ الرجاء اختيار منتج واحد على الأقل!")
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            new_order = {
                "client_name": client_name,
                "client_phone": client_phone,
                "products": selected_products,
                "total_cost": total_cost,
                "additional_discount": additional_discount,
                "final_total": final_total,
                "timestamp": timestamp
            }
            data["orders"].append(new_order)

            # **🛑 تحديث المخزون بعد الطلب**
            for item in selected_products:
                for product in data["products"]:
                    if product["name"] == item["name"]:
                        product["stock"] -= item["quantity"]  # **تحديث المخزون**
            
            save_data(data)
            st.success("🎉 تم إنشاء الطلب بنجاح!")
            st.rerun()

    # عرض الطلبات السابقة (تمت إزالة البحث عن طلب)
    st.subheader("📋 الطلبات السابقة")
    if not data["orders"]:
        st.info("🚀 لا توجد طلبات بعد!")
    else:
        for order in data["orders"]:
            with st.expander(f"📌 طلب بتاريخ {order['timestamp']}"):
                st.write(f"👤 العميل: {order.get('client_name', 'غير محدد')}")
                st.write(f"📞 الهاتف: {order.get('client_phone', 'غير محدد')}")
                for item in order["products"]:
                    st.write(f"🛒 {item['name']} - {item['quantity']} قطعة - {item['price']} جنيه")

                st.write(f"💰 **الإجمالي:** {order['total_cost']} جنيه")
                st.write(f"📉 **بعد الخصم:** {order['final_total']} جنيه")

if __name__ == "__main__":
    orders_page()
