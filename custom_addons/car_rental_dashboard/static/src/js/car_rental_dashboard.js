/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class CarRentalDashboard extends Component {
    static template = "car_rental_dashboard.Dashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ loading: true, refreshing: false, data: null });
        onWillStart(() => this.refresh());
    }

    async refresh() {
        this.state.loading = !this.state.data;
        this.state.refreshing = true;
        try {
            this.state.data = await this.orm.call("car.rental.dashboard", "get_dashboard_data", []);
        } finally {
            this.state.loading = false;
            this.state.refreshing = false;
        }
    }

    openModel(model, domain = []) {
        return this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain,
        });
    }

    openRecord(model, id) {
        return this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            views: [[false, "form"]],
            res_id: id,
        });
    }

    createRental() {
        return this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "car.rental.order",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
        });
    }

    exportOrders() {
        return this.action.doAction("car_rental.action_export_orders_wizard");
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat(undefined, {
            style: "currency",
            currency: "IDR",
            maximumFractionDigits: 0,
        }).format(amount || 0);
    }

    get fleetGradient() {
        const fleet = this.state.data?.fleet;
        if (!fleet) {
            return "conic-gradient(#e5e7eb 0 100%)";
        }
        const total = fleet.available + fleet.rented + fleet.maintenance || 1;
        const available = fleet.available / total * 100;
        const rented = available + fleet.rented / total * 100;
        return `conic-gradient(#047857 0 ${available}%, #34d399 ${available}% ${rented}%, #fbbf24 ${rented}% 100%)`;
    }
}

registry.category("actions").add("car_rental_dashboard.dashboard", CarRentalDashboard);
