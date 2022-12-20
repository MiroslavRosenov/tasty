
function validateSignupName(name){
    if (name === null || name.length < 6){
        return false;
    }
    return true;
}

function validateSignupEmail(email){
    const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (email === null || email.length === 0 || !re.test(email)){
        return false;
    }
    return true;
}

function validateSignupPassword(password){
    if (password === null || password.length < 8){
        return false;
    }
    return true;
}

function signupInputHandler(){
    let firstName = document.getElementById("signup-firstName");
    let lastName = document.getElementById("signup-lastName");
    let emailBox = document.getElementById("signup-email");
    let passwordBox = document.getElementById("signup-password");
    let confirmPasswordBox = document.getElementById("signup-confirm-password");

    let alertBox = document.getElementById("alertBox")
    let alertMessage = document.getElementById("alertMessage")

    if (!validateSignupName(firstName.value)){
        alertBox.classList.remove("hidden")
        alertMessage.textContent = "Моля, въведете име от поне 6 знака!"
        return;
    }

    if (!validateSignupName(lastName.value)){
        alertBox.classList.remove("hidden")
        alertMessage.textContent = "Моля, въведете фамилия от поне 6 знака!"
        return;
    }

    if (!validateSignupEmail(emailBox.value)){
        alertBox.classList.remove("hidden")
        alertMessage.textContent = "Моля, въведете валиден имейл!"
        return;
    }
    if (!validateSignupPassword(passwordBox.value)){
        alertBox.classList.remove("hidden")
        alertMessage.textContent = "Моля, въведете парола, съдържаща поне 8 знака!"
        return;
    }
    if (passwordBox.value !== confirmPasswordBox.value){
        alertBox.classList.remove("hidden")
        alertMessage.textContent = "Паролата и потвърждението трябва да съвпадат!"
        return;
    }
    data = {
        "firstName": firstName.value, 
        "lastName": lastName.value,
        "email": emailBox.value, 
        "password": passwordBox.value
    }
    console.log(data);
    $.ajax({
        type: "POST",
        url: "/signup",
        data: JSON.stringify(data),
        success: function(resp) {
            alertBox.classList.replace("bg-green-100 rounded-lg py-5 px-6 mb-4 text-base text-green-700 mb-3")
            alertMessage.textContent = resp["message"]
        },
        error: function(error){
            alertBox.classList.remove("hidden")
            alertMessage.textContent = error["responseJSON"]["error"]
        }
    })
}