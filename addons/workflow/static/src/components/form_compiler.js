import { patch } from "@web/core/utils/patch";
import { FormCompiler } from "@web/views/form/form_compiler";
import { createElement } from "@web/core/utils/xml";


patch(FormCompiler.prototype ,{
    
    compileHeader(el, params){
        let res = super.compileHeader(el, params);

        // check xem res có Field nào không
        const hasFieldTag = res.querySelector("Field") !== null;

        if (!hasFieldTag) {
            let statusbarAndButton = createElement("StatusbarAndButton");
            return statusbarAndButton;
        } else {
            return res;
        }
        
    }
});