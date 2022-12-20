function storeUser(data){
    const state = Boolean(data.auth_id !== null)
}

function getDish(){
    return window.location.href.split("/dishes/")[1]
}

function likeDish(element){
    $.ajax({
        type: "POST",
        url: "http://localhost:8000/likeDish",
        data: JSON.stringify(likeData),
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
        type: "POST",
        url: "http://localhost:8000/unlikeDish",
        data: JSON.stringify(likeData),
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
    let countLikes = document.getElementById("dish-page-num-likes");
    if("WATCH_DISH_ID" in window.localStorage){
        let dish_id = window.localStorage.getItem("WATCH_DISH_ID");
        $.ajax({
            type: "POST",
            url: "http://localhost:8000/countLikes",
            data: JSON.stringify({"dish_id": dish_id}),
            success: function(res) {
                data = JSON.parse(res);
                countLikes.textContent = data["likes"];
            },
            error: function(error){
                console.log("Error");
                console.log(JSON.stringify(error));
            }
        });
    }
}

function initializeLikeButton(){
    let likeButton = document.getElementById("dish-page-like-btn");
    // likeButton.setAttribute("fill", "#FFFFFF");

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
// displayLikesCount();
// populateDishDetails();
// populateDishComments();