/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { formatMonetary } from "@web/views/fields/formatters";

export class CustomAccountPaymentPopOver extends Component {
    static props = { '*': { optional: true } };
    static template = "payment_module.AccountPaymentPopOver";

    setup() {
        // ✅ Đảm bảo state luôn có giá trị mặc định
        this.state = useState({ actualAmountPaidFormatted: "0.0" });

        // ✅ Chạy trước khi component render để tránh lỗi
        onWillStart(async () => {
            const formattedAmount = this.formatActualAmountPaid();
            this.state.actualAmountPaidFormatted = formattedAmount;
        });
    }

    formatActualAmountPaid() {
        console.log("📌 Gọi formatActualAmountPaid() với dữ liệu:", this.props.record?.data);
        
        if (!this.props.record || !this.props.record.data) {
            console.warn("⚠️ Không có dữ liệu record hoặc record.data");
            return "0.00";
        }
    
        const amount = this.props.record.data.actual_amount_paid || 0;
        const currencyId = this.props.record.data.actual_currency_id?.[0] || null;
    
        console.log("✅ Giá trị actual_amount_paid:", amount);
        console.log("✅ ID tiền tệ actual_currency_id:", currencyId);
    
        return formatMonetary(amount, { currencyId }) || "0.00";
    }
    
}

// ✅ Đăng ký vào registry
registry.category("components").add("payment_module.AccountPaymentPopOver", CustomAccountPaymentPopOver);
console.log("✅ Custom AccountPaymentPopOver Registered Successfully!");