from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api



class AuditTrailForm(forms.Form):
    #az = forms.ChoiceField(label=_("Availability Zone"),
    #                         required=False,
    #                         help_text=_("Choose AZ"))
    #az is in the json...
    host = forms.ChoiceField(label=_("Compute Host"),
                             required=False,
                             help_text=_("Choose a Host"))
    tenant = forms.ChoiceField(label=_("Tenant"),
                             required=False,
                             help_text=_("Choose a Tenant"))
                           
    instances = forms.ChoiceField(label=_("VM's"),
                             required=False,
                             help_text=_("Choose a VM"))
    start = forms.DateField(input_formats=("%Y-%m-%d",))
    end = forms.DateField(input_formats=("%Y-%m-%d",))
    
                             
    def __init__(self, request, *args, **kwargs):
        super(AuditTrailForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial', {})
      
        self.fill_hosts_and_geo_tags(request)
        self.fields['tenant'].choices = self.populate_tenants(request)
        #self.fields['az'].choices = self.populate_az(request)
        
    def populate_az(self, request):
        try:
             az = api.nova.availability_zone_list(request)
             az_list = [('','---')]
             #az has hosts also associated to avoiv ajax if changed
             az_list.extend([(x.zoneName, x.zoneName) for x in az])
             return az_list
        except Exception as e:
            exceptions.handle(request,
                              _('Unable to retrieve AZs.'))
        return []
        
    def populate_tenants(self, request):
        try:
             tenants = api.keystone.tenant_list(request)
             tenant_list = [('', '---')]
             tenant_list.extend([(x.id, x.name) for x in tenants[0]])
             return tenant_list
        except Exception as e:
            exceptions.handle(request,
                              _('Unable to retrieve tenants.'))
        return []
    
    def fill_hosts_and_geo_tags(self, request):
        try:
            nova_geotags = api.nova.geotags_list(request)
            cinder_geotags = api.cinder.geo_tag_list(request)
            hosts = [('', '---')]
            hosts.extend([(x.server_name, x.server_name) for x in  nova_geotags + cinder_geotags])
            
            self.fields['host'].choices = hosts
            
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve geo tags.'))
        
    #TODO Add CLEAN
    