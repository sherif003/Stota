import streamlit as st
import datetime
from data_handler import load_data, save_data

def refund_page():
    st.title("🔄 إدارة المرتجعات")

    # تحميل البيانات
    data = load_data()

    # التأكد من وجود طلبات قابلة للاسترجاع
    if not data["orders"]:
        st.info("🚀 لا توجد طلبات مسجلة!")
        return

    # اختيار الطلب المراد استرجاعه
    order_options = {f"📌 {order['timestamp']} - {order['final_total']} جنيه": order for order in data["orders"]}
    selected_order_label = st.selectbox("📋 اختر الطلب للاسترجاع", list(order_options.keys()))

    if selected_order_label:
        selected_order = order_options[selected_order_label]

        # عرض تفاصيل الطلب
        st.subheader("📋 تفاصيل الطلب")
        st.write(f"👤 **العميل:** {selected_order.get('client_name', 'غير محدد')}")
        st.write(f"📞 **رقم الهاتف:** {selected_order.get('client_phone', 'غير محدد')}")
        st.write(f"💰 **الإجمالي:** {selected_order['total_cost']} جنيه")
        st.write(f"📉 **بعد الخصم:** {selected_order['final_total']} جنيه")
        st.write("📦 **المنتجات في الطلب:**")

        for item in selected_order["products"]:
            st.write(f"🛒 {item['name']} - {item['quantity']} قطعة - {item['price']} جنيه")

        # زر تأكيد استرجاع الطلب
        if st.button("🚨 تأكيد حذف الطلب واسترجاع المخزون"):
            # **استرجاع المخزون**
            for item in selected_order["products"]:
                for product in data["products"]:
                    if product["name"] == item["name"]:
                        product["stock"] += item["quantity"]  # إعادة الكمية المسترجعة إلى المخزون
            
            # إزالة الطلب من قائمة الطلبات
            data["orders"].remove(selected_order)
            
            # حفظ التعديلات
            save_data(data)

            st.success("✅ تم استرجاع الطلب واستعادة المخزون بنجاح!")
            st.rerun()

if __name__ == "__main__":
    refund_page()
