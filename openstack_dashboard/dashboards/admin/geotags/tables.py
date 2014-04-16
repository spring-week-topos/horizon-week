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

from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.aggregates import constants

def gt_valid_invalid(obj):
    #if we need more data, then setup obj.geo_tag on the services
    #as before...
    #(licostan) Ideally the api should return {} or None, to defined after PoC.
    if not hasattr(obj, 'geo_tag'):
        return '---'
    #in case that returns None
    if not obj.geo_tag:
        return "---"
    return obj.geo_tag[0]['valid_invalid']


class NovaGeoTagsTable(tables.DataTable):

    STATUS_CHOICES = (
        ("Valid", None),
        ("Invalid", None),
        ("---", None)
    )
    serve_name = tables.Column('server_name', verbose_name=_('Server Name'))
    valid_invalid = tables.Column(gt_valid_invalid, status=True,
                                  status_choices=STATUS_CHOICES,
                                  verbose_name=_('Geo Tag Valid'))
    mac_address = tables.Column('mac_address', verbose_name=_('MAC Address'))
    plt_latitude = tables.Column('plt_latitude', verbose_name=_('Latitude'))
    plt_longitude = tables.Column('plt_longitude', verbose_name=_('Longitude'))


    class Meta:
        name = "nova"
        verbose_name = _("Nova Geo Tags")

class CinderGeoTagsTable(tables.DataTable):
    serve_name = tables.Column('server_name', verbose_name=_('Server Name'))
    valid_invalid = tables.Column('valid_invalid', verbose_name=_('Valid - Invalid'))
    mac_address = tables.Column('mac_address', verbose_name=_('MAC Address'))
    plt_latitude = tables.Column('plt_latitude', verbose_name=_('Latitude'))
    plt_longitude = tables.Column('plt_longitude', verbose_name=_('Longitude'))


    class Meta:
        name = "cinder"
        verbose_name = _("Cinder Geo Tags")