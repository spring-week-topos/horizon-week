horizon.geotags = {
   jit_data: [],
   current_node: 0,
   selected_node: null,
   status: false, // when finish loading set true to avoid flicker
   icons: {
     'cnode': '/static/dashboard/img/server-gray.svg',
     'snode': '/static/dashboard/img/db-gray.svg',
     'rack': '/static/dashboard/img/rack.svg',
     'row': '/static/dashboard/img/row.svg',
     'slot': '/static/dashboard/img/slot.svg',
     'room': '/static/dashboard/img/room.svg',
     'dcenter': '/static/dashboard/img/datacenter.png',
   
   },
   
   reset: function() {
         horizon.geotags.jit_data = [];
	 horizon.geotags.current_node = 0;
	 horizon.geotags.selected_node = null;
   },
	 
   set_status: function(stat) {
   
       horizon.geotags.status = stat;
   },
   
   create_node: function(id, label, image, extra, color, dim, shape) {
     var dim = dim || 20;
         
     node_name = '';
     shape = shape || "square";
     if( image ) { 
       shape = "image";
       node_name = label;
       label = '';
     }
    
     node = { id: id,
              name: label,
	      data: { 
	         "node_name": node_name, //for images
	         "image": image,
	         "info": extra,
		 "$color": color,
		 "$type": shape,
	         "$dim": dim },
	      adjacencies: [],
	     }
	     
    horizon.geotags.jit_data.push(node);
    node.index_pos = horizon.geotags.current_node++;
    return node;
   },
   link_nodes: function( src_node, target_node, color, force_node) {
    //if want to use an external array
    node = force_node || horizon.geotags.jit_data[src_node.index_pos] 
    
    var color = color || "#909291";
    edge = { nodeTo: target_node.id, 
             nodeFrom: src_node.id,
	     data: { 
	      "$color": color,
	     }}
    node.adjacencies.push( edge )
			     
   },

   build_hyper_info: function( data ) {
       
	hv_info = data.hv;
	if(  !hv_info || !hv_info.cpu_info){
	  return "";
	 }
	cpu = JSON.parse(hv_info.cpu_info);
        cpu_info = "CPU: " + cpu.vendor + "|" + cpu.model + "|" + cpu.arch 

	memory_info = "Used Memory MB: " + hv_info.memory_mb_used + "<br>" + "Total Memory MB: " + hv_info.memory_mb;
	vcpus = "vCPUs Used: " + hv_info.vcpus_used;
        return  cpu_info + "<br>" + memory_info + "<br>" + vcpus + "<br>" + " IP: " + hv_info.host_ip;


	
	
   },
   //this code is repeated and good for reactoring.
   iterate_and_link: function( parent, childs ) {
   
   },
   
   create_dc_topology: function( data ) {
          var selected_path =  "dc#" + data.dc_number + "_room#" + data.room_number + "_row#" + data.row_number + "rack_#" + data.rack_number + "slot#";

          var root_node = horizon.geotags.create_node('dc#' + data.dc_number, 'Data Center #' + data.dc_number,  
                            horizon.geotags.icons['dcenter'], 'Compute Nodes: ' + data.total_compute + '<br>' + 'Storage Nodes: ' + data.total_storage,
                            "#8899FF", 64)

          $.each(data.topology, function(room, row) {
	      var roomNode = horizon.geotags.create_node( root_node.id + '_room#' + room, 
                                 'Room #' + room, 
				 horizon.geotags.icons['room'], 
				 "", "#8899FF", 48)
	    horizon.geotags.link_nodes(root_node, roomNode, '#000000');
            $.each( row, function(row, rack) {
         
                 var rowNode = horizon.geotags.create_node(
		                            roomNode.id + '_row#' + row,
					    'Row #' + row,
					    horizon.geotags.icons['row'], "", "#99bbFF", 36)
		
		horizon.geotags.link_nodes(roomNode, rowNode, '#3366FF')
	 	 
	        $.each( rack, function(rack, slots) {
                       var rackNode = horizon.geotags.create_node( rowNode.id + 'rack_#' + rack,
	                                           'Rack #' + rack,
						   horizon.geotags.icons['rack'], "",
						   "#8899FF", 48)

                      horizon.geotags.link_nodes(rowNode, rackNode,  '#3399FF');
	
	
	      $.each( slots, function(slot, services) {
	                var slotNode = horizon.geotags.create_node( rackNode.id + 'slot#' + slot,
			                           'Slot #' + slot, 
						   horizon.geotags.icons['slot'], "", "#8899FF", 48)
		        horizon.geotags.link_nodes(rackNode, slotNode, '#33CCFF');
			if( slotNode.id ==  selected_path + slot) {
			       horizon.geotags.selected_node = slotNode;
			
                        }
			

	          $.each(services, function(idx, nodes)  {
	            for(var i=0; i < nodes.length; i++) {
		        obj = nodes[i];
			data = JSON.parse(obj.data);
			info = '';
		        if( idx == 'compute')  {
		            img = horizon.geotags.icons['cnode'];
			    info = horizon.geotags.build_hyper_info(data);
			}
			else {
			    img = horizon.geotags.icons['snode'];
			  }
			  
		        if( data.valid != 'Valid') {
			   color = "#FC1900";
			} else {
			   color = "#64F50A";
			}
			var  nd  = horizon.geotags.create_node(
			         slotNode + '#node_' + obj.name,
				 obj.name,
				 img,
				 info,
				 color, 48)
			
			horizon.geotags.link_nodes(slotNode, nd, color)
					     
		    }
		    
		 })
	       })
	     })
         })
     })

	return horizon.geotags.jit_data;
   
   
   },

   register_custom_shapes: function() {
     
	$jit.ForceDirected.Plot.NodeTypes.implement({ 
	'image': { 
	            'render': function(node, canvas){
		      
		       var ctx = canvas.getCtx(); 
		       var img = new Image(); 
		       var pos = node.getPos(); 
		       img.src= node.data.image;
		       var dim = node.getData('dim');
		       if( horizon.geotags.status == false ) {
		           img.onload = function() {
			   
			      ctx.drawImage(img, pos.x-16, pos.y-16, dim, dim);
			     
			      ctx.fillText(node.data.node_name, pos.x, pos.y + dim);
			   };
		       } else {
		             ctx.drawImage(img, pos.x-16, pos.y-16, dim, dim);
			     ctx.fillText(node.data.node_name, pos.x, pos.y+dim);
		       }
		       
		       
		       },
		    'contains':
                           function(node,pos){ 
                                       var npos = node.pos.getc(true); 
				       dim = node.getData('dim'); 
				       return this.nodeHelper.square.contains(npos, pos, dim); 
                          } 
	           }, 
	
	   });
   
   },
}

horizon.addInitFunction(function () {
 //jit must be loaded first
 horizon.geotags.register_custom_shapes();
});



