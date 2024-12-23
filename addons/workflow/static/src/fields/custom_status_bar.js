import { useService } from "@web/core/utils/hooks";
import { onWillStart, useState } from "@odoo/owl";
import { StatusBarField } from "@web/views/fields/statusbar/statusbar_field";
import { patch } from "@web/core/utils/patch";

// Solution 1: Extend the StatusBarField component to handle the status bar
patch(StatusBarField.prototype, {

    setup() {
        super.setup(...arguments);
        this.model = this.env.model.config.resModel;
        this.id = this.env.model.config.resId;
        this.orm = useService('orm');
        this.selection_items = useState({});


        onWillStart(async () => {
            const workflows = await this.orm.searchRead('custom.workflow', [['model_id.model', '=', this.model]], ['id']);

            if (workflows.length > 0) {
                const stateRecords = await this.orm.searchRead('custom.workflow.state', [['workflow_id', '=', workflows[0].id]], ['name', 'priority']);
                stateRecords.sort((a, b) => b.priority - a.priority);
                const state_record = await this.orm.searchRead('custom.state.record', [['model_id.model', '=', this.model], ['res_id', '=', this.id]], ['current_state'], { limit: 1 });
                if (state_record && state_record.length > 0) {
                    this.selection_items = stateRecords.map(state => ({
                        value: state.name,
                        label: state.name,
                        isSelected: state.name === state_record[0].current_state,  
                    }));         
                }
            }     
        });
    },

    
    async onStateChange() {
        console.log(await this.selection_items)

        const currentStateIndex = this.selection_items.findIndex(state => state.isSelected);
        this.selection_items[currentStateIndex].isSelected = false;
        const nextStateIndex = currentStateIndex + 1;

        if (nextStateIndex < this.selection_items.length) {
            this.selection_items[nextStateIndex].isSelected = true;
            await this.orm.call('custom.workflow', 'action_approve', [this.id, this.model]);
        }
    },
});


