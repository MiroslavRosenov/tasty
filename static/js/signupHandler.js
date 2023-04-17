function nameValidation(name){
    if (name === null || name.length < 2){
        return false;
    }
    return true;
}

function emailValidation(email){
    const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (email === null || email.length === 0 || !re.test(email)){
        return false;
    }
    return true;
}

function passwordValidation(password){
    if (password === null || password.length < 8){
        return false;
    }
    return true;
}

function signupInputHandler(){
    const firstName = document.getElementById("signup-firstName");
    const lastName = document.getElementById("signup-lastName");
    const emailBox = document.getElementById("signup-email");
    const passwordBox = document.getElementById("signup-password");
    const confirmPasswordBox = document.getElementById("signup-confirm-password");

    var notyf = new Notyf({
        duration: 2000,
        position: {
            x: "right",
            y: "top",
        }
    });

    if (!nameValidation(firstName.value)){
        notyf.error("Моля, въведете име от поне 2 знака!");
    } 
    else if (!nameValidation(lastName.value)){
        notyf.error("Моля, въведете фамилия от поне 2 знака!");
    } 
    else if (!emailValidation(emailBox.value)){
        notyf.error("Моля, въведете валиден имейл!");
    } 
    else if (!passwordValidation(passwordBox.value)){
        notyf.error("Моля, въведете парола, съдържаща поне 8 знака!");
    }
    else if (passwordBox.value !== confirmPasswordBox.value){
        notyf.error("Паролата и потвърждението трябва да съвпадат!");
    }
    else {
        const data = {
            "firstName": firstName.value, 
            "lastName": lastName.value,
            "email": emailBox.value, 
            "password": passwordBox.value
        }

        $.ajax({
            type: "POST",
            url: "/signup",
            data: JSON.stringify(data),
            beforeSend: function() {            
                $("#sumbitButton").prop("disabled", true)
            },
            success: function(resp) {
                notyf.success(resp["message"]);
            },
            error: function(error){
                notyf.error(error["responseJSON"]["error"]);
            },
            complete: function(data) {
                $("#sumbitButton").prop("disabled", false);
            }
        })
    }
}