import streamlit as st
import datetime
from data_handler import load_data, save_data

def orders_page():
    st.title("🛒 إدارة الطلبات")

    # تحميل البيانات
    data = load_data()

    # **🆕 إنشاء أو تعديل طلب**
    order_options = ["إنشاء طلب جديد"] + [f"طلب بتاريخ {order['timestamp']}" for order in data["orders"]]
    selected_order = st.selectbox("📋 اختر الطلب", order_options)

    # **تحضير بيانات الطلب**
    if selected_order == "إنشاء طلب جديد":
        order_index = None
        client_name, client_phone, selected_products, additional_discount = "", "", {}, 0.0
    else:
        order_index = order_options.index(selected_order) - 1
        existing_order = data["orders"][order_index]
        client_name = existing_order.get("client_name", "")
        client_phone = existing_order.get("client_phone", "")
        selected_products = {item["name"]: item for item in existing_order["products"]}
        additional_discount = float(existing_order.get("additional_discount", 0.0))

        # ✅ **إعادة الكميات السابقة إلى المخزون قبل التعديل**
        for item in existing_order["products"]:
            for product in data["products"]:
                if product["name"] == item["name"]:
                    product["stock"] += item["quantity"]

    # **إدخال بيانات العميل**
    client_name = st.text_input("👤 اسم العميل", client_name)
    client_phone = st.text_input("📞 رقم الهاتف", client_phone)

    # **🔍 اختيار المنتجات**
    st.subheader("📦 اختر المنتجات")
    product_names = [product["name"] for product in data["products"]]
    selected_product_names = st.multiselect("📦 المنتجات", product_names, default=list(selected_products.keys()))

    updated_products = {}

    for product_name in selected_product_names:
        product = next(p for p in data["products"] if p["name"] == product_name)
        default_quantity = selected_products.get(product_name, {}).get("quantity", 1)

        quantity = st.number_input(
            f"🔢 الكمية من {product['name']} (متوفر: {product['stock']})",
            min_value=0, max_value=product["stock"] + default_quantity, step=1, value=default_quantity
        )

        if quantity > 0:
            updated_products[product["name"]] = {
                "name": product["name"],
                "price": product["final_price"],
                "quantity": quantity
            }

    # **تطبيق الخصم الإضافي**
    additional_discount = st.number_input("💵 خصم إضافي", min_value=0.0, step=0.01, format="%.2f", value=additional_discount)

    # **حساب الإجمالي**
    total_cost = sum(item["price"] * item["quantity"] for item in updated_products.values())
    final_total = max(0, total_cost - additional_discount)

    st.write(f"💰 **إجمالي السعر:** {total_cost:.2f} جنيه")
    st.write(f"📉 **بعد الخصم:** {final_total:.2f} جنيه")

    # **🔄 حفظ الطلب**
    if st.button("✅ حفظ الطلب"):
        if not updated_products:
            st.error("⚠️ يجب اختيار منتج واحد على الأقل!")
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if order_index is None else existing_order["timestamp"]

            new_order = {
                "client_name": client_name,
                "client_phone": client_phone,
                "products": list(updated_products.values()),
                "total_cost": total_cost,
                "additional_discount": additional_discount,
                "final_total": final_total,
                "timestamp": timestamp
            }

            # ✅ **تحديث المخزون بعد التعديل**
            for product in data["products"]:
                old_quantity = selected_products.get(product["name"], {}).get("quantity", 0)
                new_quantity = updated_products.get(product["name"], {}).get("quantity", 0)
                product["stock"] += old_quantity - new_quantity

            if order_index is None:
                data["orders"].append(new_order)  # إضافة طلب جديد
            else:
                data["orders"][order_index] = new_order  # تحديث الطلب الحالي

            save_data(data)
            st.success("🎉 تم حفظ التعديلات بنجاح!")
            st.rerun()

    # **عرض الطلبات السابقة**
    st.subheader("📋 الطلبات السابقة")
    if not data["orders"]:
        st.info("🚀 لا توجد طلبات بعد!")
    else:
        for i, order in enumerate(data["orders"]):
            with st.expander(f"📌 طلب بتاريخ {order['timestamp']}"):
                st.write(f"👤 العميل: {order.get('client_name', 'غير محدد')}")
                st.write(f"📞 الهاتف: {order.get('client_phone', 'غير محدد')}")
                for item in order["products"]:
                    st.write(f"🛒 {item['name']} - {item['quantity']} قطعة - {item['price']} جنيه")
                st.write(f"💰 **الإجمالي:** {order['total_cost']} جنيه")
                st.write(f"📉 **بعد الخصم:** {order['final_total']} جنيه")

if __name__ == "__main__":
    orders_page()
