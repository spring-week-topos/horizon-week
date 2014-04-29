#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import logging

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import views

import json

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.geotags \
    import constants
from openstack_dashboard.dashboards.admin.geotags \
    import tables as project_tables


LOG = logging.getLogger(__name__)
INDEX_URL = constants.GEOTAGS_INDEX_URL

def get_hyper_info(hyper_obj):
    args = ['vcpus_used', 'host_ip', 'memory_mb', 'memory_mb_used',
            'cpu_info', 'topology', 'free_ram']
    serial = {}
    for x in args:
        serial[x] = getattr(hyper_obj, x, None)
    return serial

def serialize_server(obj, additional_attrs=None):
    base_attrs = {'indoor': 'loc_or_error_msg', 
                  'name': 'server_name', 
                  'valid': 'valid_invalid',
                  'latitude': 'plt_latitude', 
                  'longitude': 'plt_longitude', 
                  'type': 'service_type'}
    #service_type do not exists here.......
    
    if additional_attrs:
        base_attrs.update(additional_attrs)
        
    serialized = {}
    for x,y in base_attrs.iteritems():
        serialized[x] = getattr(obj, y, '')
        
    return serialized

def serialize_server_hv(obj):
    return serialize_server(obj, {'hv': 'hypervisor_info'})

class IndexView(tables.DataTableView):
    table_class = project_tables.GeoTagsTable
    template_name = constants.GEOTAGS_TEMPLATE_NAME

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        
        context["points"] = json.dumps(self.get_all_geotags(), 
                                       default=serialize_server,
                                       sort_keys=True, indent=4)
        return context

    def get_all_geotags(self):
        request = self.request
        geotags = []
        try:
            nova_geotags = api.nova.geotags_list(self.request)
            cinder_geotags = api.cinder.geo_tag_list(self.request)
            for novatag in nova_geotags:
                setattr(novatag, 'service_type', 'nova')
                geotags.append(novatag)
            for cindertag in cinder_geotags:
                setattr(cindertag, 'service_type', 'cinder')
                geotags.append(cindertag)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve geo tags.'))

        return geotags

    def get_data(self):
        return self.get_all_geotags()


class DataCenterView(views.APIView):
    template_name = constants.DATACENTER_TEMPLATE_NAME

    def _parse_location(self, obj, map_dc, stype='compute'):
        #ugly, slow... refactor
        
        try:
            (room, row, rack, slot) = obj.loc_or_error_msg.split("-")[1:5]
        except ValueError:
            LOG.error('Cannot parse invalid location string')
            return

        if not map_dc.get(room):
            map_dc[room] = {}
        if not map_dc.get(room).get(row):
            map_dc[room][row] = {}

        if not map_dc[room][row].get(rack):
            map_dc[room][row][rack] = {}

        if not map_dc[room][row][rack].get(slot):
            map_dc[room][row][rack][slot] = {}

        if not map_dc[room][row][rack][slot].get(stype):
            map_dc[room][row][rack][slot][stype] = []

        nodes = map_dc[room][row][rack][slot][stype]

        if not hasattr(obj, 'hypervisor_info'):
            obj.hypervisor_info = {}
        
        json_data = json.dumps(obj, 
                               default=serialize_server_hv,
                               sort_keys=True, indent=4)
                               
        new_node = {'name': getattr(obj, 'server_name', ''),
                    'data': json_data}

        nodes.append(new_node)

    def _build_graph_structure(self, compute_by_dc, storage_by_dc):
        #only for one dcenter, if not use a dict per dc #
        map_dc = {}
        for x in compute_by_dc:
            self._parse_location(x, map_dc)
        for x in storage_by_dc:
            self._parse_location(x, map_dc, "storage")
        return map_dc

    def get(self, request, *args, **kwargs):
        data = {}
        looking_dc = kwargs.get('datacenter')

        if not looking_dc or len(looking_dc) < 5:
            raise Exception('Missing data center')
        looking_room = looking_dc.split("-")[1]
        looking_row = looking_dc.split("-")[2]
        looking_rack = looking_dc.split("-")[3]
        looking_slot = looking_dc.split("-")[4]
        looking_dc = looking_dc.split("-")[0]

        #TODO(someone) add filter by room or something in the api,
        #right now is a pure string.... (refactor db)
        try:
            nova_geotags = api.nova.geotags_list(self.request)
            cinder_geotags = api.cinder.geo_tag_list(self.request)
            compute_by_dc = [x for x in nova_geotags
                                if x.loc_or_error_msg.startswith(looking_dc)]
            storage_by_dc = [x for x in cinder_geotags
                                if x.loc_or_error_msg.startswith(looking_dc)]

            #filter not supported
            hypervisor_list = api.nova.hypervisor_list(request)
            hypervisors = dict((x.hypervisor_hostname.lower(), x)
                                    for x in hypervisor_list)
            #we can use sum or other python functions, but have to
            #iterate anyways so...
            compute_capacity = {'total_vcpus': 0,
                                'total_memory': 0,
                                'used_memory': 0,
                                'running_vms': 0,
                                'used_vcpus': 0}
            
            for x in compute_by_dc:
                #it will be accessible by javascript, can show the brand Intel
                #for #instance
                hyp = hypervisors.get(x.server_name.lower(), {})
                x.hypervisor_info = get_hyper_info(hyp)
                if not hyp:
                    continue
                #use a list and for...
                compute_capacity['total_memory'] += hyp.memory_mb
                compute_capacity['used_memory'] += hyp.memory_mb_used
                compute_capacity['used_vcpus'] += hyp.vcpus_used
                compute_capacity['running_vms'] += hyp.running_vms
            
            data = {'topology': self._build_graph_structure(compute_by_dc,
                                                            storage_by_dc),
                    'total_compute': len(compute_by_dc),
                    'total_storage': len(storage_by_dc),
                    'dc_number': looking_dc,
                    'room_number': looking_room,
                    'row_number': looking_row,
                    'rack_number': looking_rack,
                    'slot_number': looking_slot,
                    'compute_capacity': compute_capacity
                    }

        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve geo tags.'))

        return self.render_to_response({'topology_data': json.dumps(data)})
