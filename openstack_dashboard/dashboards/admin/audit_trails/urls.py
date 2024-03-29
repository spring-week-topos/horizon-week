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

from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.dashboards.admin.audit_trails \
    import views


urlpatterns = patterns('openstack_dashboard.dashboards.admin.audit_trails.views',
        url(r'^$', views.IndexView.as_view(), name='index'),
        url(r'report_view$', views.ReportView.as_view(), name='report'),
        url(r'tenant_vms/(?P<tenant_id>[^/]+)$', views.GetTenantVmsView.as_view(), name='tenant_vms'),
    
)
