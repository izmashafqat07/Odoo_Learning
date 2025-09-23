odoo.define('obesystem.peo_button', function (require) {
    "use strict";

    const ListController = require('web.ListController');
    const viewRegistry = require('web.view_registry');
    const ListView = require('web.ListView');
    const core = require('web.core');
    const rpc = require('web.rpc');

    const PEOListController = ListController.extend({
        buttons_template: 'obesystem.PEOListView.Buttons',

        events: Object.assign({}, ListController.prototype.events, {
            'click .o_button_publish_all': '_onPublishAllClick',
        }),

        _onPublishAllClick() {
            rpc.query({
                model: 'obesystem.peo',
                method: 'action_publish_all',
                args: [],
            }).then(() => {
                this.reload();
            });
        },
    });

    const PEOListView = ListView.extend({
        config: Object.assign({}, ListView.prototype.config, {
            Controller: PEOListController,
        }),
    });

    viewRegistry.add('peo_list_view', PEOListView);
});
