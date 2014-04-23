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

from django.core.urlresolvers import reverse
from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import messages
from horizon import tables
from horizon.utils import memoized

import json
import urllib2

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.geotags \
    import constants

LOG = logging.getLogger(__name__)

class UpdateRow(tables.Row):
    ajax = True
    ajax_poll_interval = 10000
    classes = ['no-progress-bar']
    TAG_SERVICE = {'nova': api.nova.geo_tag_show,
                   'cinder': api.cinder.geo_tag_show}
                       
    def get_data(self, request, geotag_id):
        service_type = geotag_id.split("#")[1]
        tag_id = geotag_id.split("#")[0]
        try:
            geo_tag = UpdateRow.TAG_SERVICE[service_type](request, tag_id)
            setattr(geo_tag, 'service_type', service_type)
            return geo_tag
        except Exception as e:
            messages.error(request, e)


def get_service_type(geotag):
    cinder_template_name = 'admin/geotags/_cinder_service_type.html'
    nova_template_name = 'admin/geotags/_nova_service_type.html'
    if geotag.service_type == 'cinder':
        return template.loader.render_to_string(cinder_template_name)
    else:
        return template.loader.render_to_string(nova_template_name)


def get_rack_slot(geotag):
    if geotag.loc_or_error_msg:
        data = geotag.loc_or_error_msg.split(constants.ROOM_ROW_RACK_DELIMITER)
        return "DC: " + data[0] + ", Room: " + data[1] + ", Row: " + data[2] + ", Rack: " + data[3] + ", Slot: " + data[4]
    return '---'

@memoized.memoized_method
def get_country_from_lat_long(longitude, lat):
    try:
        data = json.load(urllib2.urlopen('http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false'
                                     % (lat, longitude)))
    except Exception as e:
        LOG.error('cannot get country code %s' % e)
        data = None
        
    if not data or not data.get('results'):
        return '---'
    
    for result in data['results']:
        for component in result['address_components']:
            if 'country' in component['types']:
                return component['long_name']
    return '---'

def get_country_code(geotag):
    return get_country_from_lat_long(geotag.plt_latitude, geotag.plt_longitude)


def get_datacenter_link(datum):
    return reverse(constants.DATACENTER_INDEX_URL,
                   kwargs={'datacenter': datum.loc_or_error_msg})


class GeoTagsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Valid", None),
        ("Invalid", None),
        ("---", None)
    )
    server_name = tables.Column('server_name', verbose_name=_('Server Name'))
    service_type = tables.Column(get_service_type,
                                 verbose_name=_('Service Type'))
    valid_invalid = tables.Column('valid_invalid', status=True,
                                  status_choices=STATUS_CHOICES,
                                  verbose_name=_('Geo Tag Valid'))
    country_code = tables.Column(get_country_code,
                                 verbose_name=_('Country Code'))
    rack_slot = tables.Column(get_rack_slot, verbose_name=_('Datacenter Location Info'),
                              link=get_datacenter_link)
    power_state = tables.Column('power_state', verbose_name=_('Power state'))
    
    def get_object_id(self, obj):
        return "%s#%s" % (obj.id, obj.service_type)

    
    class Meta:
        name = "geotags"
        verbose_name = _("Geo Tags Inventory")
        row_class = UpdateRow
        status_columns = ['valid_invalid']
