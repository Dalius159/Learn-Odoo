import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";
import { StatusbarAndButton } from "./statusbar_and_button";

patch(FormRenderer, {
    components : {
        ...FormRenderer.components,
        StatusbarAndButton
    }
});