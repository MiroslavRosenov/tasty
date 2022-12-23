function populateRecentPostedDishes(data) {
    let postSection = document.getElementById("home-posts");
    
    while (postSection.firstChild) {
        postSection.removeChild(postSection.firstChild);
    }

    data.forEach(dish => {
        // Card div
        let postCard = document.createElement("div");
        postCard.id = dish["id"];
        postCard.className = "rounded overflow-hidden shadow-lg cursor-pointer transition duration-500 ease-in-out transform hover:-translate-y-1 hover:scale-105 ...";
        postCard.onclick = () => {
            window.location.href = `/dishes/${dish["id"]}`
        }

        // Image
        let dishImage = document.createElement("img");
        dishImage.className = "w-full h-64 object-cover";
        dishImage.src = dish["imageUrl"];
        dishImage.alt = dish["title"];

        // Text div
        let textDiv = document.createElement("div");
        textDiv.className = "px-6 py-4";
        let titleText = document.createElement("div");
        titleText.className = "font-medium text-center mb-2 overflow-ellipsis overflow-hidden whitespace-nowrap ...";
        titleText.textContent = dish["title"];
        textDiv.appendChild(titleText);

        // Tag div
        let tagDiv = document.createElement("div");
        tagDiv.className = "px-6 pb-2";
        
        let tag = document.createElement("span");
        tag.className = "inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2 mb-2 overflow-hidden overflow-ellipsis ..."
        tag.textContent = Array.from(JSON.parse(dish["ingredients"])).join(", ")
        tagDiv.appendChild(tag);

        postCard.appendChild(dishImage);
        postCard.appendChild(textDiv);
        // postCard.appendChild(tagDiv);
        postSection.appendChild(postCard);
    })
}

function fetchDishes(){
    $.ajax({
        type: "GET",
        url: "/api/recentRecipes",
        success: function(res) {
            document.getElementById("home-no-posts").classList.add("hidden")
            populateRecentPostedDishes(res["results"]);
        },
        error: function(error){
            document.getElementById("home-no-posts").classList.remove("hidden")
        }
    })
}

function onSearchChange(element){
    if (element.target.value === ""){
        fetchDishes();
        return;
    }

    tag.setDisabled(true);
    $.ajax({
        type: "POST",
        url: "/api/searchRecipe",
        data: JSON.stringify({"ingredients": JSON.parse(element.target.value)}),
        success: function(data) {
            console.log(data["results"])
            if (data["results"] === undefined) {
                document.getElementById("home-no-posts").classList.remove("hidden")
                populateRecentPostedDishes([]);
            }
            else {
                document.getElementById("home-no-posts").classList.add("hidden")
                populateRecentPostedDishes(data["results"]);
            }
        },
        error: function(error){
            console.log(JSON.stringify(error));
        },
        complete: function(data) {
            tag.setDisabled(false);
        }
    })
}

let input = document.querySelector("input[name=tags]");
let tag = new Tagify(input, {editTags: false});
input.addEventListener("change", onSearchChange)

fetchDishes();