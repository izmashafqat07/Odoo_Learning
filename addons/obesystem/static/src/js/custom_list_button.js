/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListController } from "@web/views/list/list_controller";

export class CustomListController extends ListController {
    /**
     * Override create button rendering
     */
    get buttons() {
        const buttons = super.buttons;
        const addBtn = buttons?.find((b) => b.name === "create");

        if (addBtn) {
            addBtn.title = "Add New"; // hover tooltip
            addBtn.icon = "fa fa-plus"; // FontAwesome icon
            addBtn.label = ""; // text hata do
            addBtn.class = (addBtn.class || "") + " rounded-circle custom-add-btn";
        }
        return buttons;
    }
}

// Register controller
registry.category("views").add("list", {
    ...registry.category("views").get("list"),
    Controller: CustomListController,
});
