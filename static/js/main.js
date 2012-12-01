 $(document).ready(function(){
    "use strict";
    var labels = $("label");
    if (!Modernizr.input.placeholder) {
        labels.show(); 
    }
 });