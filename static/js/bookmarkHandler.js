function getDish(){
    return parseInt(window.location.href.split("/dishes/")[1])
}

function addDish(element){
    $.ajax({
        type: "PUT",
        url: "/api/bookmarks",
        data: JSON.stringify({"id": getDish()}),
        success: function(res) {
            element.setAttribute("fill", "#EC4899");
            displayCount();
        },
        error: function(error){
            alertBox.classList.remove("hidden")
            alertMessage.textContent = error["responseJSON"]["error"]
        }
    });
}

function removeDish(element){
    $.ajax({
        type: "DELETE",
        url: "/api/bookmarks",
        data: JSON.stringify({"id": getDish()}),
        success: function(res) {
            element.setAttribute("fill", "#FFFFFF");
            displayCount();
        },
        error: function(error){
            alertBox.classList.remove("hidden")
            alertMessage.textContent = error["responseJSON"]["error"]
        }
    });
}

function toggleButton() {
    let icon = document.getElementById("fav-icon");
    
    if (icon.getAttribute("fill") === "#FFFFFF"){
        addDish(icon);
    }
    else {
        removeDish(icon);
    }
}

function displayCount(){
    let bookmarks = document.getElementById("dish-page-num-likes");
    
    $.ajax({
        type: "POST",
        url: "/api/bookmarksCount",
        data: JSON.stringify({"id": getDish()}),
        success: function(resp) {
            bookmarks.textContent = resp["count"];
        }
    });
}

function bookmarkButton(){    
    $.ajax({
        type: "POST",
        url: "/api/bookmarks",
        data: JSON.stringify({"id": getDish()}),
        success: function(resp) {
            if (resp["state"] === true){
                document.getElementById("fav-icon").setAttribute("fill", "#EC4899");
            }
        }
    });
}

let alertBox = document.getElementById("alertBox")
let alertMessage = document.getElementById("alertMessage")

let button = document.getElementById("fav-button")
button.addEventListener("click", toggleButton)

bookmarkButton();
displayCount();
