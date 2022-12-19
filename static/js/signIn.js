function validateLoginEmail(email){
    const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (email === null || email.length === 0 || !re.test(email)){
        return false;
    }
    return true;
}

function validateLoginPassowrd(password){
    if (password === null || password.length < 8){
        return false;
    }
    return true;
}

function loginInputHandler(){
    let emailBox = document.getElementById("login-email");
    let passwordBox = document.getElementById("login-password");

    let alertBox = document.getElementById("alertBox")
    let alertMessage = document.getElementById("alertMessage")

    if (!validateLoginEmail(emailBox.value)){
        alertBox.classList.remove("hidden")
        alertMessage.textContent = "Моля, въведете валиден имейл"
        return;
    }
    if (!validateLoginPassowrd(passwordBox.value)){
        alertBox.classList.remove("hidden")
        alertMessage.textContent = "Моля, въведете валидна парола"
        return;
    }
    
    data = {
        "email": emailBox.value,
        "password": passwordBox.value
    };
    $.ajax({
        type: "POST",
        url: "/api/signin",

        data: JSON.stringify(data),
        success: function(resp) {
            window.location.href = "/";
        },
        error: function(error){            
            alertBox.classList.remove("hidden")
            alertMessage.textContent = error["responseJSON"]["error"]
        }
    })
}