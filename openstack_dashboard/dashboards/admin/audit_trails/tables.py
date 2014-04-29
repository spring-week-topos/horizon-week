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
import decimal
import logging
import re

from django.core.urlresolvers import reverse
from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import messages
from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.audit_trails \
    import constants

LOG = logging.getLogger(__name__)


#propense to fail.......
def get_server_name(datum):
    return datum[5]

def get_event_name(datum):
    return datum[4]

def get_date(datum):
    return datum[2]

def get_task_state(datum):
    return datum[6]

def get_az(datum):
    return datum[9]

def get_geo_tags(datum):
    return datum[10]

def get_instance(datum):
    return datum[11]


class AuditTrailTable(tables.DataTable):
    
    verbose_name = "Event Table"
    
    event_date = tables.Column(get_date, verbose_name=_('Date'))
    server_name = tables.Column(get_server_name, verbose_name=_('Server Name'))
    az = tables.Column(get_az, verbose_name=_('AZ'))
    geo_tags = tables.Column(get_geo_tags, verbose_name=_('Geo Tags'))
    event_name  = tables.Column(get_event_name, verbose_name=_('Event Name'))
    task_state  = tables.Column(get_task_state, verbose_name=_('Task State'))
    instance_state  = tables.Column(get_instance, verbose_name=_('Instance'))
    
    def get_object_id(self, obj):
        return obj[0]
    
    def has_more_data(self):
        return self.filtered_data 
    
    def get_pagination_string(self):
        #change for pagination-param instead of offset
        params = re.sub(r".*\?", "", self.get_full_url())
        marker = self.get_marker()
        url = re.sub(r"\&?offset=\d+&?", "", params)
        url += "&offset=" + str(marker)
        return url
    
    def get_marker(self):
        return str(int(self.request.GET.get('offset', 0)) + 1  * 50)
        
    
    class Meta:
        name = ""
        pagination_param = "offset"