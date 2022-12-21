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

function toggleButton(element) {
    if (element.getAttribute("fill") === "#FFFFFF"){
        addDish(element);
    }
    else {
        removeDish(element);
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
    let likeButton = document.getElementById("dish-page-like-btn");
    
    $.ajax({
        type: "POST",
        url: "/api/bookmarks",
        data: JSON.stringify({"id": getDish()}),
        success: function(resp) {
            if (resp["state"] === true){
                likeButton.setAttribute("fill", "#EC4899");
            }
        }
    });
}

let alertBox = document.getElementById("alertBox")
let alertMessage = document.getElementById("alertMessage")

bookmarkButton();
displayCount();
