import streamlit as st
from data_handler import load_data, save_data

def products_page():
    st.title("🛍️ إدارة المنتجات")

    data = load_data()

    with st.form("add_product_form"):
        product_name = st.text_input("📌 اسم المنتج")
        stock = st.number_input("📦 المخزون", min_value=0, step=1)
        original_price = st.number_input("💰 السعر الأصلي", min_value=0.0, step=0.01)
        selling_price = st.number_input("🏷️ السعر بعد البيع", min_value=0.0, step=0.01)
        
        # Fixed discount amount
        discount_value = st.number_input("💵 قيمة الخصم", min_value=0.0, step=0.01)
        final_price = max(0, selling_price - discount_value)

        submitted = st.form_submit_button("✅ إضافة المنتج")

        if submitted:
            new_product = {
                "name": product_name,
                "stock": stock,
                "original_price": original_price,
                "selling_price": selling_price,
                "discount_value": discount_value,
                "final_price": final_price,
                "profit_per_unit": final_price - original_price,
                "sold": 0
            }
            data["products"].append(new_product)
            save_data(data)
            st.success("🎉 تم إضافة المنتج بنجاح!")
            st.rerun()

    st.subheader("📋 المنتجات الحالية")

    if not data["products"]:
        st.info("🚀 لا توجد منتجات مضافة بعد!")
    else:
        for product in data["products"]:
            with st.expander(f"📌 {product['name']}"):
                new_name = st.text_input("📌 اسم المنتج", product["name"], key=f"name_{product['name']}")
                new_stock = st.number_input("📦 المخزون", min_value=0, step=1, value=product["stock"], key=f"stock_{product['name']}")
                new_original_price = st.number_input("💰 السعر الأصلي", min_value=0.0, step=0.01, value=product["original_price"], key=f"orig_price_{product['name']}")
                new_selling_price = st.number_input("🏷️ السعر بعد البيع", min_value=0.0, step=0.01, value=product["selling_price"], key=f"sell_price_{product['name']}")

                new_discount_value = st.number_input("💵 قيمة الخصم", min_value=0.0, step=0.01, value=product["discount_value"], key=f"disc_value_{product['name']}")
                
                # Recalculate final price & profit
                new_final_price = max(0, new_selling_price - new_discount_value)
                new_profit_per_unit = new_final_price - new_original_price

                st.write(f"📊 **السعر بعد الخصم:** {new_final_price:.2f} EGP")
                st.write(f"💰 **الربح لكل وحدة:** {new_profit_per_unit:.2f} EGP")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 حفظ التعديلات", key=f"save_{product['name']}"):
                        product.update({
                            "name": new_name,
                            "stock": new_stock,
                            "original_price": new_original_price,
                            "selling_price": new_selling_price,
                            "discount_value": new_discount_value,
                            "final_price": new_final_price,
                            "profit_per_unit": new_profit_per_unit
                        })
                        save_data(data)
                        st.success("✅ تم حفظ التعديلات!")
                        st.rerun()
                with col2:
                    if st.button("🗑️ حذف المنتج", key=f"delete_{product['name']}"):
                        data["products"].remove(product)
                        save_data(data)
                        st.success("🗑️ تم حذف المنتج!")
                        st.rerun()
