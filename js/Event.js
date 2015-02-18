
function tab1(){
		document.getElementById("load").style.display="block";

    		var t1 = setTimeout(function(){
		
    	    		document.getElementById("sec1").style.display="none";
			document.getElementById("tab2").style.display="none";    		
			document.getElementById("menu").style.display="none";

			document.getElementById("tab1").style.display="block";
    			},2000);

			findlowest("tab1");

	}





function tab2(){
		
    	document.getElementById("sec1").style.display="none";
    	document.getElementById("tab1").style.display="none";
    	document.getElementById("menu").style.display="none";
    	
		document.getElementById("load").style.display="block";

    		var t1 = setTimeout(function(){
		


			document.getElementById("tab2").style.display="block";
    			},2000);

    		findlowest("tab2");
		}





function tab3(){
		document.getElementById("load").style.display="block";

    		var t1 = setTimeout(function(){
    	    		document.getElementById("sec1").style.display="none";
    		
			document.getElementById("tab2").style.display="none";

			document.getElementById("tab1").style.display="none";
			document.getElementById("menu").style.display="block";
			
   		 },2000);

    		findlowest("menu");
 				
	}


function tab4(){
	document.getElementById("load").style.display="block";

    		var t1 = setTimeout(function(){
		
    	   		 document.getElementById("sec1").style.display="none";
    			document.getElementById("menu").style.display="none";
			document.getElementById("tab1").style.display="none";
			document.getElementById("tab2").style.display="block";
    			},2000);
			findlowest("tab2");		

		}





function tab5(){
	document.getElementById("load").style.display="block";

   		 var t1 = setTimeout(function(){
		
    	    		document.getElementById("sec1").style.display="none";
    			document.getElementById("tab2").style.display="none";
			document.getElementById("menu").style.display="none";
			document.getElementById("tab1").style.display="block";

    		},2000);

}

function findlowest(index){

		var vals = $('#'+index+' tr td:nth-child(5)').map(function () {

    var x=$(this).text();


    var y=x.split("$");


    return y[1];
    }).get();
	var min = Math.min.apply(Math, vals);
    

    $('#'+index+' tr td:nth-child(5) ').filter(function () {
    
	return $(this).text() === "$"+min;
    

}).addClass("lowest");
}



