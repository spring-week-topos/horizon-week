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

from horizon import messages
from horizon import tables

from openstack_dashboard import api


class CinderServicesUpdateRow(tables.Row):
    ajax = True
    ajax_poll_interval = 10000

    def get_data(self, request, geo_tag_id):
        try:
            return api.cinder.geo_tag_show(request, geo_tag_id)
        except Exception as e:
            messages.error(request, e)

class NovaServicesUpdateRow(tables.Row):
    ajax = True
    ajax_poll_interval = 10000

    def get_data(self, request, geo_tag_id):
        try:
            return api.nova.geo_tag_show(request, geo_tag_id)
        except Exception as e:
            messages.error(request, e)

class NovaGeoTagsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Valid", None),
        ("Invalid", None),
        ("---", None)
    )
    server_name = tables.Column('server_name', verbose_name=_('Server Name'))
    valid_invalid = tables.Column('valid_invalid', status=True,
                                  status_choices=STATUS_CHOICES,
                                  verbose_name=_('Geo Tag Valid'))
    mac_address = tables.Column('mac_address', verbose_name=_('MAC Address'))
    plt_latitude = tables.Column('plt_latitude', verbose_name=_('Latitude'))
    plt_longitude = tables.Column('plt_longitude', verbose_name=_('Longitude'))

    class Meta:
        name = "nova"
        verbose_name = _("Nova Geo Tags")
        row_class = NovaServicesUpdateRow
        status_columns = ['valid_invalid']

class CinderGeoTagsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Valid", None),
        ("Invalid", None),
        ("---", None)
    )
    server_name = tables.Column('server_name', verbose_name=_('Server Name'))
    valid_invalid = tables.Column('valid_invalid', status=True,
                                  status_choices=STATUS_CHOICES,
                                  verbose_name=_('Geo Tag Valid'))
    mac_address = tables.Column('mac_address', verbose_name=_('MAC Address'))
    plt_latitude = tables.Column('plt_latitude', verbose_name=_('Latitude'))
    plt_longitude = tables.Column('plt_longitude', verbose_name=_('Longitude'))

    class Meta:
        name = "cinder"
        verbose_name = _("Cinder Geo Tags")
        row_class = CinderServicesUpdateRow
        status_columns = ['valid_invalid']