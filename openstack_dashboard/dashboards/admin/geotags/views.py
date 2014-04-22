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
import urllib2

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.geotags \
    import constants
from openstack_dashboard.dashboards.admin.geotags \
    import tables as project_tables


LOG = logging.getLogger(__name__)
INDEX_URL = constants.GEOTAGS_INDEX_URL


class IndexView(tables.DataTableView):
    table_class = project_tables.GeoTagsTable
    template_name = constants.GEOTAGS_TEMPLATE_NAME

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["points"] = json.dumps(self.get_all_geotags(), default=lambda o: {"indoor": o.loc_or_error_msg, "name": o.server_name, "valid": o.valid_invalid, "latitude": o.plt_latitude, "longitude" : o.plt_longitude, "type": o.service_type}, sort_keys=True, indent=4)
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
        print dir(geotags[0])
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
        nodes.append({'name': obj.server_name})

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

        if not looking_dc:
            raise Exception('Missing data center')

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
            data = self._build_graph_structure(compute_by_dc, storage_by_dc)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve geo tags.'))

        return self.render_to_response({'dc_map': json.dumps(data)})
