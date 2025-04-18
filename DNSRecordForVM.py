from extras.scripts import *

from netbox_dns.choices import RecordStatusChoices
from netbox_dns.models import Record, Zone
from tenancy.models import Tenant

class DNSRecordForVM(Script):

    class Meta:
        name = "DNS Record for Virtual Machine"
        description = "Script to run in Event Rule for changes on Virtual Machine to manage DNS records"


    def run(self, data, commit):
        info = []
        if data['tenant'] is not None:
            tenant = Tenant.objects.get(name=data['tenant']['name'])
            zone = Zone.objects.get(id=tenant.custom_field_data['dns_zone'])
            name = data['name'].split('.')[0]


            if data['primary_ip4'] is not None:
                a_record, a_created = Record.objects.update_or_create(
                    name=name,
                    zone=zone,
                    type="A",
                    defaults={
                        "value": data['primary_ip4']['address'].split('/')[0],
                        "tenant": tenant,
                        "status": RecordStatusChoices.STATUS_ACTIVE
                    }
                )
                if a_created:
                    self.log_success(f"Created new DNS record: {a_record}")
                    info.append(a_record.name)
                else:
                    self.log_info(f'Record exists: {a_record.name}')
            else:
                self.log_info(f'VM {name} has no primary IPv4, skipping A record')

            if data['primary_ip6'] is not None:
                aaaa_record, aaaa_created = Record.objects.update_or_create(
                    name=name,
                    zone=zone,
                    type="AAAA",
                    defaults={
                        "value": data['primary_ip6']['address'].split('/')[0],
                        "tenant": tenant,
                        "status": RecordStatusChoices.STATUS_ACTIVE
                    }
                )
                if aaaa_created:
                    self.log_success(f"Created new DNS record: {aaaa_record}")
                    info.append(aaaa_record.name)
                else:
                    self.log_info(f'Record exists: {aaaa_record}')
            else:
                self.log_info(f"VM {name} has no primary IPv6, skipping AAAA record")
        else:
            self.log_info(f"VM {name} has no tenant assigned, skipping")

        return info
