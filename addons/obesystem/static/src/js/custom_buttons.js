/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

patch(ListController.prototype, {
    setup() {
        // pehle parent setup call karo
        super.setup();
    },

    get buttons() {
        const btns = super.buttons;
        if (btns) {
            btns.forEach((btn) => {
                if (btn.string === "New") {
                    btn.string = "";       // text remove
                    btn.icon = "fa-plus"; // icon add
                }
            });
        }
        return btns;
    },
});
