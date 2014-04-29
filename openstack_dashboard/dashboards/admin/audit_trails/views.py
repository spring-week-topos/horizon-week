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
import calendar
import json
import logging
import requests
import time

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response  # noqa
from django.views.generic import View as generic_view  # noqa
from django.http import HttpResponse  # noqa

from horizon import exceptions
from horizon import tables
from horizon import views

from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.audit_trails \
    import constants
from openstack_dashboard.dashboards.admin.audit_trails \
    import forms as audit_forms
from openstack_dashboard.dashboards.admin.audit_trails \
    import tables as audit_tables


LOG = logging.getLogger(__name__)
INDEX_URL = constants.AUDIT_TRAIL_INDEX_URL

STACKTACH = getattr(settings, 'STACKTACH_URL', 'http://localhost:19000')


# Stolen from stacktach/datetime_to_decimal.py
def dt_to_decimal(adate):
    return calendar.timegm(time.strptime(adate + ' 00:00', '%m/%d/%Y %H:%M'))


#move to api
def search_stacktash(field, value, service='nova', start_date=None,
                     end_date=None, offset=0):
    params = {'service': service}
    if field and value:
        params['field'] = field
        params['value'] = value

    params['limit'] = 50
    params['offset'] = offset
    if start_date and end_date:
        params['when_min'] = dt_to_decimal(start_date)
        params['when_max'] = dt_to_decimal(end_date)

    results = requests.get(STACKTACH + ("/stacky/search/"), params=params)
    if results.content:
        return results.json()
    return None


class ReportView(tables.DataTableView):
    table_class = audit_tables.AuditTrailTable
    template_name = constants.AUDIT_TRAIL_REPORT_TEMPLATE_NAME

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        context["report_title"] = self.title
        return context

    def get_data(self):
        #TODO(someone): Instantiate form with post data
        #and call valid! instead of this manual process
        #ex Form(self.request.POST), etc
        #refactor also, dupicated code

        #az = self.request.POST.get('az') or None
        host = self.request.GET.get('host') 
        tenant = self.request.GET.get('tenant')
        vm = self.request.GET.get('instances')
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end') 
        offset = self.request.GET.get('offset', 0)

        data = []
        field = None
        value = None
        partial = 'All'
        if vm:
            field = 'instance'
            value = vm
            partial = ' VM: ' + vm
        elif tenant:
            field = 'tenant'
            value = tenant
            #move to template
            partial = ' Tenant ' + tenant
        elif host:
            field = 'host'
            value = host
            partial = ' Host ' + host
        try:
            self.title = 'Report for %s' % partial
            if start_date and end_date:
                self.title += ' From %s To %s' % (start_date, end_date)
            data = search_stacktash(field, value, start_date=start_date,
                                     end_date=end_date, offset=offset)
            if not data:
                return []
            data.pop(0)
        except Exception:
            exceptions.handle(self.request,
                        _('Unable to retrieve audit trail report.'))

        return data


class IndexView(views.APIView):
    form_class = audit_forms.AuditTrailForm
    template_name = constants.AUDIT_TRAIL_TEMPLATE_NAME

    def get(self, request, *args, **kwargs):
        form = IndexView.form_class(request)
        return self.render_to_response({'daily_form': form})


class GetTenantVmsView(generic_view):
    """
    Required to update vms per tenant on ajax select-box change
    #TODO(someone) Check if admin policy is being applied!
    
    ONLY WORK FOR ACTIVE VM'S. IDEALLY STACTASH SHOULD RETURN THE LIsT
    OF VM's recorded
    """

    def get(self, request, *args, **kwargs):
        #TODO(bug?)  nova api ignore tenant_id

        tenant = kwargs.get('tenant_id')
        vms = []
        try:
            instances = api.nova.server_list(request, project_id=tenant)
            vms = dict((x.id, x.name) for x in instances[0]
                          if x.tenant_id == tenant)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve vms.'))
        return HttpResponse(json.dumps(vms), content_type='text/json')
