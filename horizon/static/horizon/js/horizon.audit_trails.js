horizon.audit_trails = {
  
}
horizon.addInitFunction(function () {
 
  function update_tenant_change(field) {
      var $this = $(field),
      base_type = $this.val();
      console.log(base_type)
      if( !base_type) {
           $("#id_instances").html("");
	   return;
      }
     //retrieve VMs tru ajax
    $.ajax({
      url: 'tenant_vms/' + base_type,
      method: 'get',
      success: function(response_body) {
        options = "<option value=''>---</option>";
        for(var instance in response_body) {
	   options += "<option value='" + instance + "'>" + response_body[instance] + "</option>";
	}
	
	$("#id_instances").html(options);
	
      },
      error: function(response) {
          horizon.clearErrorMessages();
          horizon.alert('error', gettext('There was a problem communicating with the server, please try again.'));
      }
    }); 
      
    
  }
  
  function disable_select(field, disable_ids, enable_ids) {
       /* if value == '---' or empty, invert disable/enable */
       
        var value = $(field).val();
       
        disable_val = true;
	enable_val = false;
        if( !value || value === '---')
	{
	   disable_val = false;
	   enable_val = true;
	}
        $(field).prop('disabled', false);
        if( disable_ids ) {
	   for(var x in disable_ids) {
	      $(disable_ids[x]).prop('disabled', disable_val);
	   }
	}
	if( enable_ids ) {
	   for(var x in enable_ids) {
	   $(enable_ids[x]).prop('disabled', enable_val);
	   }
	}
		
  }

  
  $(document).on('change', '#id_tenant', function (evt) {
     disable_select(this, ['#id_host'], ['#id_instances']);
     update_tenant_change(this);
   });
   $(document).on('change', '#id_host', function (evt) {
     disable_select(this, ['#id_tenant', '#id_instances']);
      
   });
 
  horizon.forms.datepicker();
});
