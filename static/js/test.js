document.querySelector("button").onclick = function(){

    var svgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    svgRect.setAttributeNS(null, "x", Math.random() * 100);
    svgRect.setAttributeNS(null, "y", Math.random() * 100);
    svgRect.setAttributeNS(null, "width", 50);
    svgRect.setAttributeNS(null, "height", 50);
    svgRect.setAttributeNS(null, "fill", "darkblue");
    
    document.querySelector("svg").appendChild(svgRect);  

};