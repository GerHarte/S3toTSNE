d3.json('/getData', function(error, sampleData) {


    var width =   parseInt(d3.select("#app-tsnearea").style("width"), 10);
    var height =   $(window).height() - 60 ;



    var xScale = d3.scale.linear()
    				 .domain([  d3.min(sampleData, function(d) { return d.x; }),
    							d3.max(sampleData, function(d) { return d.x; })])
    				 .range([10, width]);
    				 
    var yScale = d3.scale.linear()
    				 .domain([  d3.min(sampleData, function(d) { return d.y; }), 
    							d3.max(sampleData, function(d) { return d.y; })])
    				 .range([10, height]);

    var sizeScale = d3.scale.linear()
             .domain([  1, 10])
             .range([16, 100]);


    var svg = d3.select("#app-tsnearea")
    		.append("svg:svg")
    			.attr("height", height)
    			.attr("width", width)
    		.append("g")
    			.call(d3.behavior.zoom().x(xScale).y(yScale).on("zoom", zoom)); 
    		;


    svg.append("rect")
    	 .attr("class", "overlay")
    	 .attr("width", width)
    	 .attr("height", height);
     


    var circle = svg.selectAll("circle")
    		.data(sampleData)
    		.enter()
        .append("svg:image")
           .attr("xlink:href", function(d) { return d.path;})
           .attr("x", "-8px")
           .attr("y", "-8px")
           .attr("width", "16px")
           .attr("height", "16px")
           .attr("transform", transform);
                


    function zoom() {
      circle.attr("transform", transform);
      circle.attr("width", scale_img);
      circle.attr("height", scale_img);

    }

    function transform(d) {
      return "translate(" + xScale(d.x) + "," + yScale(d.y) + ")";
    }

    function scale_img(d) {
      return sizeScale(d3.event.scale);
    }



});

