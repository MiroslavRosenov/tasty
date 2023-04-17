$.ajax({
    type: "GET",
    url: "/api/topIngredients",
    success: function(res) {
        var chart = new ApexCharts(
            document.getElementById("ingredientsChart"),
            {
                chart: {
                    type: "donut",
                    height: "100%"
                },
                series: res["data"],
                labels: res["labels"],
                plotOptions: {
                    pie: {
                        expandOnClick: false
                    },
                },
                legend: {
                    show: true,
                    position: "right",
                }
            }
        );
        chart.render();
    },
    error: function(error){
        console.log(error)
    }
})

$.ajax({
    type: "GET",
    url: "/api/topLiked",
    success: function(res) {
        var chart = new ApexCharts(
            document.getElementById("likesChart"),
            {
                chart: {
                    type: "donut",
                    height: "100%"
                },
                series: res["data"],
                labels: res["labels"],
                plotOptions: {
                    pie: {
                        expandOnClick: false
                    }
                },
                legend: {
                    show: true,
                    position: "left",
                }
            }
        );
        chart.render();
    },
    error: function(error){
        console.log(error)
    }
})