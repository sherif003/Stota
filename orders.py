import streamlit as st
import datetime
from data_handler import load_data, save_data

def orders_page():
    st.title("🛒 إدارة الطلبات")

    data = load_data()

    # **إضافة طلب جديد**
    st.subheader("🆕 إنشاء طلب جديد")
    client_name = st.text_input("👤 اسم العميل")
    client_phone = st.text_input("📞 رقم الهاتف")

    product_names = [product["name"] for product in data["products"]]
    selected_product_names = st.multiselect("📦 اختر المنتجات", product_names)

    selected_products = {}
    for product_name in selected_product_names:
        product = next(p for p in data["products"] if p["name"] == product_name)
        quantity = st.number_input(
            f"🔢 الكمية من {product['name']} (متوفر: {product['stock']})",
            min_value=1, max_value=product["stock"], step=1, value=1
        )
        selected_products[product_name] = {"name": product["name"], "price": product["final_price"], "quantity": quantity}

    additional_discount = st.number_input("💵 خصم إضافي", min_value=0.0, step=0.01, format="%.2f")

    total_cost = sum(item["price"] * item["quantity"] for item in selected_products.values())
    final_total = max(0, total_cost - additional_discount)

    st.write(f"💰 **إجمالي السعر:** {total_cost:.2f} جنيه")
    st.write(f"📉 **بعد الخصم:** {final_total:.2f} جنيه")

    if st.button("✅ حفظ الطلب"):
        if not selected_products:
            st.error("⚠️ يجب اختيار منتج واحد على الأقل!")
        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_order = {
                "client_name": client_name,
                "client_phone": client_phone,
                "products": list(selected_products.values()),
                "total_cost": total_cost,
                "additional_discount": additional_discount,
                "final_total": final_total,
                "timestamp": timestamp
            }

            # تحديث المخزون بعد إضافة الطلب
            for item in selected_products.values():
                product = next(p for p in data["products"] if p["name"] == item["name"])
                product["stock"] -= item["quantity"]

            data["orders"].append(new_order)
            save_data(data)
            st.success("🎉 تم إنشاء الطلب بنجاح!")
            st.rerun()

    # **عرض الطلبات السابقة مع إمكانية تعديلها مباشرة**
    st.subheader("📋 الطلبات السابقة")
    if not data["orders"]:
        st.info("🚀 لا توجد طلبات بعد!")
    else:
        for i, order in enumerate(data["orders"]):
            with st.expander(f"📌 طلب بتاريخ {order['timestamp']}", expanded=False):
                client_name = st.text_input(f"👤 اسم العميل (طلب {i+1})", order["client_name"], key=f"name_{i}")
                client_phone = st.text_input(f"📞 رقم الهاتف (طلب {i+1})", order["client_phone"], key=f"phone_{i}")

                # **إرجاع الكميات القديمة إلى المخزون قبل أي تعديل**
                for item in order["products"]:
                    product = next(p for p in data["products"] if p["name"] == item["name"])
                    product["stock"] += item["quantity"]  # استرجاع المخزون

                selected_product_names = st.multiselect(
                    f"📦 المنتجات (طلب {i+1})", product_names,
                    default=[p["name"] for p in order["products"]],
                    key=f"products_{i}"
                )

                updated_products = {}
                for product_name in selected_product_names:
                    product = next(p for p in data["products"] if p["name"] == product_name)
                    default_quantity = next((p["quantity"] for p in order["products"] if p["name"] == product_name), 1)

                    quantity = st.number_input(
                        f"🔢 الكمية من {product['name']} (متوفر: {product['stock']})",
                        min_value=1, max_value=product["stock"], step=1, value=default_quantity,
                        key=f"quantity_{i}_{product_name}"
                    )
                    updated_products[product_name] = {"name": product["name"], "price": product["final_price"], "quantity": quantity}

                additional_discount = st.number_input(
                    f"💵 خصم إضافي (طلب {i+1})", min_value=0.0, step=0.01, format="%.2f",
                    value=float(order.get("additional_discount", 0.0)), key=f"discount_{i}"
                )

                total_cost = sum(item["price"] * item["quantity"] for item in updated_products.values())
                final_total = max(0, total_cost - additional_discount)

                st.write(f"💰 **إجمالي السعر:** {total_cost:.2f} جنيه")
                st.write(f"📉 **بعد الخصم:** {final_total:.2f} جنيه")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"💾 حفظ التعديلات", key=f"save_{i}"):
                        if not updated_products:
                            st.error("⚠️ يجب اختيار منتج واحد على الأقل!")
                        else:
                            updated_order = {
                                "client_name": client_name,
                                "client_phone": client_phone,
                                "products": list(updated_products.values()),
                                "total_cost": total_cost,
                                "additional_discount": additional_discount,
                                "final_total": final_total,
                                "timestamp": order["timestamp"]
                            }

                            # **إعادة تحديث المخزون بعد التعديلات**
                            for product in data["products"]:
                                product_name = product["name"]
                                old_quantity = next((p["quantity"] for p in order["products"] if p["name"] == product_name), 0)
                                new_quantity = updated_products.get(product_name, {}).get("quantity", 0)
                                product["stock"] += old_quantity - new_quantity  # استرجاع ثم خصم جديد

                            data["orders"][i] = updated_order
                            save_data(data)
                            st.success("✅ تم تحديث الطلب بنجاح!")
                            st.rerun()

                with col2:
                    confirm_delete = st.checkbox("🛑 تأكيد حذف الطلب", key=f"delete_{i}", value=True)
                    if st.button(f"🗑️ حذف الطلب", key=f"remove_{i}"):
                        if confirm_delete:
                            # **استعادة المخزون عند الحذف**
                            for item in order["products"]:
                                product = next(p for p in data["products"] if p["name"] == item["name"])
                                product["stock"] += item["quantity"]  # إرجاع الكميات فقط مرة واحدة

                            del data["orders"][i]
                            save_data(data)
                            st.success("✅ تم حذف الطلب بنجاح واسترجاع المخزون!")
                            st.rerun()
                        else:
                            st.warning("⚠️ يجب تأكيد الحذف أولاً!")

if __name__ == "__main__":
    orders_page()
