function getDish(){
    return parseInt(window.location.href.split("/dishes/")[1])
}

function likeDish(element){
    $.ajax({
        type: "PUT",
        url: "/api/bookmarks",
        data: JSON.stringify({"id": getDish()}),
        success: function(res) {
            element.setAttribute("fill", "#EC4899");
            displayLikesCount();
        },
        error: function(error){
            console.log("Error");
            console.log(JSON.stringify(error));
        }
    });
}

function unlikeDish(element){
    $.ajax({
        type: "DELETE",
        url: "/api/bookmarks",
        data: JSON.stringify({"id": getDish()}),
        success: function(res) {
            element.setAttribute("fill", "#FFFFFF");
            displayLikesCount();
        },
        error: function(error){
            console.log("Error");
            console.log(JSON.stringify(error));
        }
    });
}

function toggleLikeButton(element){
    if (element.getAttribute("fill") === "#FFFFFF"){
        likeDish(element);
    }
    else {
        unlikeDish(element);
    }
}

function displayLikesCount(){
    let bookmarks = document.getElementById("dish-page-num-likes");
    $.ajax({
        type: "POST",
        url: "/api/bookmarksCount",
        data: JSON.stringify({"id": getDish()}),
        success: function(resp) {
            bookmarks.textContent = resp["count"];
        },
        error: function(error){
            console.log(JSON.stringify(error));
        }
    });
}

function initializeLikeButton(){
    let likeButton = document.getElementById("dish-page-like-btn");
    
    $.ajax({
        type: "POST",
        url: "/api/bookmarks",
        data: JSON.stringify({"id": getDish()}),
        success: function(resp) {
            if (resp["state"] === true){
                likeButton.setAttribute('fill', '#EC4899');
            }
        }
    });
}

initializeLikeButton();
displayLikesCount();
