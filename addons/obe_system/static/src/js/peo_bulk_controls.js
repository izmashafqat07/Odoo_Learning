/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

function addHidden(el) {
    if (el && el.classList && !el.classList.contains("o_hidden")) {
        el.classList.add("o_hidden");
    }
}
function removeHidden(el) {
    if (el && el.classList && el.classList.contains("o_hidden")) {
        el.classList.remove("o_hidden");
    }
}
function extractResIds(selection) {
    const ids = [];
    for (const r of selection || []) {
        if (typeof r === "number") ids.push(r);
        else if (r && typeof r === "object") {
            if (typeof r.resId === "number") ids.push(r.resId);
            else if (typeof r.id === "number") ids.push(r.id);
            else if (typeof r.res_id === "number") ids.push(r.res_id);
        }
    }
    return ids;
}

const _super = patch(ListController.prototype, {
    onSelectionChanged(ev) {
        if (_super.onSelectionChanged) {
            _super.onSelectionChanged.call(this, ev);
        }
        try {
            const resModel =
                (this.props && this.props.resModel) ||
                (this.model && this.model.root && this.model.root.resModel);
            if (resModel !== "obe.peo") return;

            const root = this.el;
            if (!root) return;

            const btnPub = root.querySelector(".oe_peo_btn_publish");
            const btnUnpub = root.querySelector(".oe_peo_btn_unpublish");
            if (!btnPub || !btnUnpub) return;

            addHidden(btnPub);
            addHidden(btnUnpub);

            const selection = (this.model && this.model.root && this.model.root.selection) || [];
            const selectedIds = extractResIds(selection);
            const selectedCount = selectedIds.length;

            const modelTotal = (this.model && this.model.root && typeof this.model.root.count === "number")
                ? this.model.root.count
                : null;
            const domRowCount = root.querySelectorAll("tbody tr.o_data_row").length;

            const isAllSelected =
                selectedCount >= 2 &&
                (
                    (modelTotal !== null && modelTotal > 0 && selectedCount === modelTotal) ||
                    (domRowCount > 0 && selectedCount === domRowCount)
                );
            if (!isAllSelected) return;

            this.rpc({
                model: "obe.peo",
                method: "read",
                args: [selectedIds, ["state"]],
            }).then((records) => {
                let seenDraft = false, seenPub = false;
                for (let i = 0; i < records.length; i++) {
                    const st = records[i].state;
                    if (st === "draft") seenDraft = true;
                    else if (st === "published") seenPub = true;
                    if (seenDraft && seenPub) break;
                }
                if (seenDraft && !seenPub) {
                    removeHidden(btnPub);   // show Publish All
                    addHidden(btnUnpub);
                } else if (seenPub && !seenDraft) {
                    addHidden(btnPub);
                    removeHidden(btnUnpub); // show Unpublish All
                } else {
                    addHidden(btnPub);
                    addHidden(btnUnpub);
                }
            }).catch(() => {
                addHidden(btnPub);
                addHidden(btnUnpub);
            });
        } catch (e) {
            // never crash the webclient
        }
    },
});
