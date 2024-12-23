import { useService } from "@web/core/utils/hooks";
import { onWillStart, useState, Component } from "@odoo/owl";


// Solution 2: Create a new component to handle the status bar and button
export class StatusbarAndButton extends Component {
    static template = "workflow.StatusbarAndButton";

    setup() {
        this.model = this.env.model.config.resModel;
        this.id = this.env.model.config.resId;
        this.orm = useService('orm');
        this.show_button = false;
        this.selection_items = useState([]);

        this.getAllStates();
    }


    async getAllStates() {
        // Get workflow of the current model
        const workflows = await this.orm.searchRead(
            'custom.workflow', [['model_id.model', '=', this.model]], ['id']);

        if (workflows.length > 0) {
            // Get all states of the workflow
            const stateRecords = await this.orm.searchRead(
                'custom.workflow.state', 
                [['workflow_id', '=', workflows[0].id]], 
                ['name', 'priority']);
            stateRecords.sort((a, b) => b.priority - a.priority);
            // Get the current state of the record
            const state_record = await this.orm.searchRead(
                'custom.state.record', 
                [['model_id.model', '=', this.model], 
                ['res_id', '=', this.id]], 
                ['current_state'], 
                { limit: 1 });
            // Push all states to the selection_items to render
            if (state_record && state_record.length > 0) {
                const stateArray = Object.values(stateRecords);
                const newStates = [];
                stateArray.forEach((item, index) => {
                    newStates.push({
                        value: item.name,
                        label: item.name.charAt(0).toUpperCase() + item.name.slice(1),
                        isSelected: state_record[0].current_state == item.name,
                        index: index,
                    });
                });
                this.selection_items.push(...newStates);
                this.show_button = true;     
            }
        }   
    }

    // Handle the event when the user clicks on the Approve button
    // Find the state is selected
    // Turn off the selected state and turn on the next state
    async onApprove() {
        let previousState = null;
        this.selection_items.forEach((state, index) => {
            if (state.isSelected && index > 0) {
                state.isSelected = false;
                if (previousState) {
                    this.orm.call(
                        'custom.workflow', 'action_approve', [this.id, this.model]);
                    previousState.isSelected = true;    
                }
            }
            previousState = state;
        })
    }
}