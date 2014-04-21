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

from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import messages
from horizon import tables

from openstack_dashboard import api

class UpdateRow(tables.Row):
    ajax = True
    ajax_poll_interval = 100000

    def get_data(self, request, geotag_id):
        service_type = geotag_id.split("#")[1]
        tag_id = geotag_id.split("#")[0]
        try:
            if service_type == 'nova':
                nova_geo_tag = api.nova.geo_tag_show(request, tag_id)
                setattr(nova_geo_tag, 'service_type', 'nova')
                return nova_geo_tag
            else:
                cinder_geo_tag = api.cinder.geo_tag_show(request, tag_id)
                setattr(cinder_geo_tag, 'service_type', 'cinder')
                return cinder_geo_tag
        except Exception as e:
            messages.error(request, e)


def get_service_type(geotag):
    cinder_template_name = 'admin/geotags/_cinder_service_type.html'
    nova_template_name = 'admin/geotags/_nova_service_type.html'
    if geotag.service_type == 'cinder':
        return template.loader.render_to_string(cinder_template_name)
    else:
        return template.loader.render_to_string(nova_template_name)


class GeoTagsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Valid", None),
        ("Invalid", None),
        ("---", None)
    )
    server_name = tables.Column('server_name', verbose_name=_('Server Name'))
    service_type = tables.Column(get_service_type, verbose_name=_('Service Type'))
    valid_invalid = tables.Column('valid_invalid', status=True,
                                  status_choices=STATUS_CHOICES,
                                  verbose_name=_('Geo Tag Valid'))
    country_code = tables.Column('country_code', verbose_name=_('Country Code'))
    rack_slot = tables.Column('rack_slot', verbose_name=_('Rack slot'))
    power_state = tables.Column('power_state', verbose_name=_('Power state'))

    def get_object_id(self, obj):
        return "%s#%s" % (obj.id, obj.service_type)

    class Meta:
        name = "geotags"
        verbose_name = _("Geo Tags Inventory")
        row_class = UpdateRow
        status_columns = ['valid_invalid']