/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class VehicleStatusBadge extends Component {
    static template = "car_rental.VehicleStatusBadge";
    static props = { ...standardFieldProps };

    get label() {
        const field = this.props.record.fields[this.props.name];
        const item = field.selection.find(([k]) => k === this.props.record.data[this.props.name]);
        return item ? item[1] : this.props.record.data[this.props.name];
    }
}

registry.category("fields").add("vehicle_status_badge", {
    component: VehicleStatusBadge,
    supportedTypes: ["selection"],
});
