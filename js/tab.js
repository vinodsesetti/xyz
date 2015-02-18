function tab1(){

document.getElementById("load").style.display="block";

    		var t1 = setTimeout(function(){
		
document.getElementById("sec1").style.display="none";
document.getElementById("flight").style.display="block";
addTable();
},2000);
}





function addTable() {
    var myTableDiv = document.getElementById("flight")
    var table = document.createElement('TABLE')
    var tableBody = document.createElement('TBODY')

    table.border = '1'
    table.appendChild(tableBody);

    var heading = new Array();
    heading[0] = "Depart"
    heading[1] = "Arrive"
    heading[2] = "flight"
    heading[3] = "runnig"
    heading[4] = "firstclass"
	heading[5] = "coast"

    var stock = new Array()
    stock[0] = new Array("10.30 am", "6.30 pm", "1111", "nonstop", "$440","$690")
    stock[1] = new Array("11.30 pm", "6.40 pm", "2222", "nonstop", "$640","$640")
    stock[2] = new Array("4.30 am", "6.20 am", "3333", "nonstop", "$940","$540")
    stock[3] = new Array("6.30 pm", "3.40 am", "6666", "nonstop", "$840","$652")
    stock[4] = new Array("11.30 am", "12.00 pm", "8888", "nonstop", "$960","$952")

    //TABLE COLUMNS
    var tr = document.createElement('TR');
    tableBody.appendChild(tr);
    for (i = 0; i < heading.length; i++) {
        var th = document.createElement('TH')
        th.width = '100';
        th.appendChild(document.createTextNode(heading[i]));
        tr.appendChild(th);
    }

    //TABLE ROWS
    for (i = 0; i < stock.length; i++){

     var tr = document.createElement('TR');
        for (j = 0; j < stock[i].length; j++) {
            var td = document.createElement('TD')
            td.appendChild(document.createTextNode(stock[i][j]));
            tr.appendChild(td)
        }
        tableBody.appendChild(tr);
    }  
    myTableDiv.appendChild(table)
}
