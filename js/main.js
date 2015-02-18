$(document).ready(function(){
                $("li").click(function(){
                //change tab color 
                $(this).addClass("activeTab");
                $(this).siblings().removeClass("activeTab");
                //preloading
                
                var x="#p"+$(this).attr("id");
                $("p").hide();
                $(x).show(1).delay(500).slideUp(100);
                
                var y="#t"+$(this).attr("id");
                $("table").hide();
                $("#foot").show(1).delay(500).hide(1);
                $(y).hide(1).delay(500).show(1);
                
                $("#content").css("border-radius","0px 0px 20px 20px")
                var z="#tab"+$(this).attr("id");           


                var vals = $(''+z+' table tr td:nth-child(5)').map(function () {
                var x=$(menu).text();
                var y=x.split("$");
                return y[1];
                }).get();
          
                var min = Math.min.apply(Math, vals);           

                $(''+z+' table tr td:nth-child(5) span').filter(function () {
                return $(this).text() === "$"+min;
                }).addClass("lowest");
                })
                });
