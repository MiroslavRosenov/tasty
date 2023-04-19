$.ajax({
    type: "GET",
    url: "/api/topIngredients",
    success: function(res) {
        var chart = new ApexCharts(
            document.getElementById("ingredientsChart"),
            {
                chart: {
                    type: "donut",
                    animations: {
                        enabled: false
                    },
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
                    position: "bottom",
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
                    animations: {
                        enabled: false
                    },
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
                    position: "bottom",
                }
            }
        );
        chart.render();
    },
    error: function(error){
        console.log(error)
    }
})