/** @odoo-module **/

import { StockReportSearchPanel } from "@stock/views/search/stock_report_search_panel";
import { patch } from "@web/core/utils/patch";

// Ghi đè class StockReportSearchPanel
patch(StockReportSearchPanel.prototype, {
    setup() {
        super.setup(...arguments);
        this.selectedWarehouse = false;
        console.log("Custom StockReportSearchPanel setup called");
    },

    get warehouses() {
        const warehouses = this.env.searchModel.getWarehouses();
        return warehouses;
    },

    clearWarehouseContext() {
        this.env.searchModel.clearWarehouseContext();
        this.selectedWarehouse = null;
        console.log("Warehouse context cleared");
    },



    applyWarehouseContext(warehouse_id) {
        try {
            this.env.searchModel.applyWarehouseContext(warehouse_id);
            this.selectedWarehouse = warehouse_id;
            console.log(`Applied warehouse context for ID: ${warehouse_id}`);


            // Kiểm tra nếu `setDomain()` tồn tại, hãy sử dụng nó
            if (this.selectedWarehouse === 1) {
                this.env.searchModel._domain = [
                    ['product_type', '=', 'home_product']
                ];
                console.log("Domain đã được cập nhật: Consignment");
            } else {
                this.env.searchModel._domain = [
                    ['product_type', '=', 'consignment_product']
                ];
            }
        } catch (error) {
            console.error("Lỗi xảy ra:", error);
        }
    },

});
