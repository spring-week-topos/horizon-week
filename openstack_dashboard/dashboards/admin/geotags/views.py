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


from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.geotags \
    import constants
from openstack_dashboard.dashboards.admin.geotags \
    import tables as project_tables


INDEX_URL = constants.GEOTAGS_INDEX_URL


class IndexView(tables.DataTableView):
    table_classes = (project_tables.CinderGeoTagsTable,
                    project_tables.NovaGeoTagsTable)
    template_name = constants.GEOTAGS_TEMPLATE_NAME

    def get_nova_data(self):
        request = self.request
        geotags = []
        try:
            geotags = api.nova.geotags_list(self.request)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve host aggregates list.'))
        return geotags

    def get_cinder_data(self):
        request = self.request
        geotags = []
        try:
            geotags = api.nova.geotags_list(self.request)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve host aggregates list.'))
        return geotags