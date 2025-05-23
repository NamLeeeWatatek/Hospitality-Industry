/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { formatMonetary, formatDate } from "@web/views/fields/formatters";
import { parseDate } from "@web/core/l10n/dates";

export class CustomAccountPaymentField extends Component {
  static template = "payment_module.AccountPaymentField";
  static props = { "*": { optional: true } };

  setup() {
    this.state = useState({ actualAmountPaidFormatted: "0.0" });
    onWillStart(async () => {
      const formattedAmount = this.formatActualAmountPaid();
      this.state.actualAmountPaidFormatted = formattedAmount;
    });
  }

  formatActualAmountPaid() {

    if (!this.props.record || !this.props.record.data) {
      console.warn("⚠️ Không có dữ liệu record hoặc record.data");
      return "0.00";
    }

    const amount = this.props.record.data.actual_amount_paid || 0;
    const currencyId = this.props.record.data.actual_currency_id?.[0] || null;

    return formatMonetary(amount, { currencyId }) || "0.00";
  }
}

registry.category("fields").add("account_payment", {
  component: CustomAccountPaymentField,
  supportedTypes: ["float"],
});
