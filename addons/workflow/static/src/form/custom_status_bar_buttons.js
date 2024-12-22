import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";
import { StatusBarButtons } from "@web/views/form/status_bar_buttons/status_bar_buttons";
import { patch } from "@web/core/utils/patch";
import { StatusBarField } from "@web/views/fields/statusbar/statusbar_field";

patch(StatusBarButtons.prototype, {
    setup() {
        this.model = this.env.model.config.resModel;
        this.orm = useService('orm');
        this.show_button = false;

        onWillStart(async () => {
            const hasWorkflow = await this.orm.searchRead('custom.workflow', [['model_id.model', '=', this.model]], ['id']);

            if (hasWorkflow && hasWorkflow.length > 0) {
                this.show_button = true;
                this.statusBarFieldInstance = new StatusBarField(this);
            }   
        });
    },

    async onApprove() {
        await this.statusBarFieldInstance.onStateChange();
        // const result = await this.orm.call('custom.workflow', 'action_approve', [this.env.model.config.resId, this.model]);
        // if (result) {
        //     window.location.reload()
        // }
    },
});


