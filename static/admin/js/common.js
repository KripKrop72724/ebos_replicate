// dependant autocomplete focus on serach bar
function inputFocus(e){
    setTimeout(function(){
        input = document.getElementsByClassName("select2-search__field");
        if(input.length > 0){
            input[0].focus();
        }
    }, 500)
}

function renderELementFocus(){
    let elements = document.getElementsByClassName("select2-selection__rendered");
    for (let i = 0; i < elements.length; i++) {
        if(elements[i]){
            elements[i].addEventListener('click', inputFocus, false);
        }
    }
}

function initAutocomplete(){
    // call the `renderELementFocus` function for all select box focus
    renderELementFocus()

    // When click on inlines add button
    // again call the `renderELementFocus` for select box focus
    let add_elements = document.getElementsByClassName("grp-add-handler")
    if(add_elements){
        for (let i = 0; i < add_elements.length; i++) {
            if(add_elements[i]){
                add_elements[i].addEventListener('click', renderELementFocus, false);
            }
        }
    }
}
setTimeout(initAutocomplete, 1000);


// datepicker changeMonth and changeYear property add
grp.jQuery(function() {
    grp.jQuery('.hasDatepicker').datepicker('option', 'changeMonth', 'true');
    grp.jQuery('.hasDatepicker').datepicker('option', 'changeYear', 'true');
});
