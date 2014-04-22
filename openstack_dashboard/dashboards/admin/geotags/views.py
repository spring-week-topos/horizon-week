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


from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables

import json
import urllib2

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.geotags \
    import constants
from openstack_dashboard.dashboards.admin.geotags \
    import tables as project_tables


INDEX_URL = constants.GEOTAGS_INDEX_URL


class IndexView(tables.DataTableView):
    table_class = project_tables.GeoTagsTable
    template_name = constants.GEOTAGS_TEMPLATE_NAME

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["points"] = json.dumps(self.get_all_geotags(), default=lambda o: {"name": o.server_name, "latitude": o.plt_latitude, "longitude" : o.plt_longitude}, sort_keys=True, indent=4)
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
