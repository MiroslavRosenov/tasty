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
    const emailBox = document.getElementById("login-email");
    const passwordBox = document.getElementById("login-password");

    var notyf = new Notyf({
        duration: 2000,
        position: {
            x: "right",
            y: "top",
        }
    });

    if (!validateLoginEmail(emailBox.value)){
        notyf.error("Моля, въведете валиден имейл!");
    }
    else if (!validateLoginPassowrd(passwordBox.value)){
        notyf.error("Моля, въведете валидна парола!");
    }
    else {
        const data = {
            "email": emailBox.value,
            "password": passwordBox.value
        };
    
        $.ajax({
            type: "POST",
            url: "/signin",
            data: JSON.stringify(data),
            success: function(resp) {
                window.location.href = "/";
            },
            error: function(error){
                notyf.error(error["responseJSON"]["error"]);
            }
        })
    }
}