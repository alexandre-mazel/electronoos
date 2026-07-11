# -*- coding: utf-8 -*-

def generateTemperatureGraph(records, filename="temperature.html"):

    import json

    data = []

    for y, mo, d, h, mi, temp in records:
        data.append({
            "date": "%04d-%02d-%02d %02d:%02d" % (y, mo, d, h, mi),
            "temp": temp
        })

    jsdata = json.dumps(data)

    html = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<style>
body {
    margin:0;
    background:#f4f4f4;
    font-family:Arial;
}

#box {
    width:100%;
    height:500px;
}

canvas {
    background:white;
    width:100%;
    height:100%;
    border-radius:12px;
    box-shadow:0 3px 15px #bbb;
}

#tooltip {
    position:absolute;
    display:none;
    background:#222;
    color:white;
    padding:8px 12px;
    border-radius:8px;
    font-size:13px;
    pointer-events:none;
}
</style>

</head>

<body>

<div id="box">
<canvas id="chart"></canvas>
</div>

<div id="tooltip"></div>


<script>

var DATA = """ + jsdata + r""";

var canvas=document.getElementById("chart");
var ctx=canvas.getContext("2d");

var tip=document.getElementById("tooltip");

var points=[];

var zoom=1;


function resize(){

    canvas.width=canvas.clientWidth*devicePixelRatio;
    canvas.height=canvas.clientHeight*devicePixelRatio;

    ctx.scale(devicePixelRatio,devicePixelRatio);

    draw();
}


function color(temp,min,max){

    var v=(temp-min)/(max-min);

    v=Math.max(0,Math.min(1,v));

    var r=Math.floor(255*v);
    var b=Math.floor(255*(1-v));

    return "rgb("+r+",60,"+b+")";
}


function draw(){

    var W=canvas.clientWidth;
    var H=canvas.clientHeight;

    ctx.clearRect(0,0,W,H);


    var left=60;
    var right=25;
    var top=30;
    var bottom=50;


    var min=999;
    var max=-999;


    DATA.forEach(function(p){
        min=Math.min(min,p.temp);
        max=Math.max(max,p.temp);
    });


    if(max==min){
        max++;
        min--;
    }


    // grille

    ctx.strokeStyle="#ddd";
    ctx.lineWidth=1;

    for(var i=0;i<=5;i++){

        var y=top+i*(H-top-bottom)/5;

        ctx.beginPath();
        ctx.moveTo(left,y);
        ctx.lineTo(W-right,y);
        ctx.stroke();

        var t=max-(max-min)*i/5;

        ctx.fillStyle="#555";
        ctx.font="12px Arial";
        ctx.fillText(t.toFixed(1)+"°",5,y+4);
    }



    points=[];


    // points

    for(var i=0;i<DATA.length;i++){

        var x=left+i*(W-left-right)/(DATA.length-1);

        var y=H-bottom-
            (DATA[i].temp-min)*
            (H-top-bottom)/(max-min);

        points.push({
            x:x,
            y:y
        });
    }



    // courbe

    ctx.lineWidth=3;

    for(var i=0;i<points.length-1;i++){

        ctx.beginPath();

        ctx.strokeStyle=color(
            DATA[i].temp,
            min,
            max
        );

        ctx.moveTo(
            points[i].x,
            points[i].y
        );

        var mx=(points[i].x+points[i+1].x)/2;

        ctx.quadraticCurveTo(
            points[i].x,
            points[i].y,
            mx,
            (points[i].y+points[i+1].y)/2
        );

        ctx.stroke();
    }


    // points ronds

    DATA.forEach(function(p,i){

        ctx.fillStyle=color(p.temp,min,max);

        ctx.beginPath();
        ctx.arc(
            points[i].x,
            points[i].y,
            5,
            0,
            Math.PI*2
        );
        ctx.fill();
    });


    // axes

    ctx.strokeStyle="#444";

    ctx.beginPath();
    ctx.moveTo(left,top);
    ctx.lineTo(left,H-bottom);
    ctx.lineTo(W-right,H-bottom);
    ctx.stroke();


}


function hover(x,y){

    var best=-1;
    var dist=99999;


    for(var i=0;i<points.length;i++){

        var dx=x-points[i].x;
        var dy=y-points[i].y;

        var d=dx*dx+dy*dy;

        if(d<dist){
            dist=d;
            best=i;
        }
    }


    if(best>=0 && dist<900){

        tip.style.display="block";

        tip.style.left=(points[best].x+20)+"px";
        tip.style.top=(points[best].y)+"px";


        tip.innerHTML=
            "<b>"+
            DATA[best].temp.toFixed(1)
            +" °C</b><br>"+
            DATA[best].date;

    }
}



canvas.onmousemove=function(e){

    var r=canvas.getBoundingClientRect();

    hover(
        e.clientX-r.left,
        e.clientY-r.top
    );
};


canvas.ontouchmove=function(e){

    var r=canvas.getBoundingClientRect();

    hover(
        e.touches[0].clientX-r.left,
        e.touches[0].clientY-r.top
    );

    e.preventDefault();
};


window.onresize=resize;

resize();

</script>

</body>
</html>
"""

    open(filename,"w").write(html)

    return filename