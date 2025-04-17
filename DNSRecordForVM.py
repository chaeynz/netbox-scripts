from extras.scripts import *

from netbox_dns.choices import RecordStatusChoices
from netbox_dns.models import Record
from tenancy.models import Tenant


class DNSRecordForVM(Script):

    class Meta:
        name = "DNS Record for Virtual Machine"
        description = "Script to run in Event Rule for changes on Virtual Machine to manage DNS records"



    def run(self, data, commit):
        tenant_zone = Tenant.objects.get(name=data['tenant']['name'])
        return tenant_zone
        record = Record(
            name=data['name'].split('.')[0],
            zone=tenant_zone,
            type="A",
            value=data['primary_ip4']['address'],
            status=RecordStatusChoices.STATUS_ACTIVE
        )
        record.save()
        self.log_success(f"Created new DNS record: {record}")

        return record
