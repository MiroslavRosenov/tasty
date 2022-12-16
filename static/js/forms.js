document.querySelectorAll("input").forEach(element => {
    element.addEventListener("invalid", function(event) {
        if (event.target.validity.valueMissing) {
            event.target.setCustomValidity("Моля, попълнете това поле!");
        }
    })

    element.addEventListener("change", function(event) {
        event.target.setCustomValidity("");
    })
});