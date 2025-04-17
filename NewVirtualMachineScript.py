from extras.scripts import *
from django.utils.text import slugify

from virtualization.choices import VirtualMachineStatusChoices
from virtualization.models import Cluster, VirtualMachine
from dcim.models import Platform
from ipam.models import Prefix
from tenancy.models import Tenant


class NewVirtualMachineScript(Script):

    class Meta:
        name = "New Virtual Machine"
        description = "Provision a new VM"

    vm_name = StringVar(
        description="Name of the new VM",
        required=True
    )
    vm_count = IntegerVar(
        description="Number of VMs to create",
        required=True,
        default=1
    )
    prefix = ObjectVar(
        description="Subnet where the VMs will be deployed",
        model=Prefix
    )
    cluster= ObjectVar(
        description="Cluster to deploy this VM on",
        model=Cluster,
        default="RC"
    )
    platform = ObjectVar(
        description="OS to install in the VM",
        model=Platform,
        default="Debian"
    )
    tenant = ObjectVar(
        description="Tenant of the VM",
        model=Tenant,
        default=Tenant.objects.get(name='vPulse').pk
    )

    def run(self, data, commit):

        # Create virtual machines
        for i in range(1, data['vm_count'] + 1):
            vm = VirtualMachine(
                name=f"{data['vm_name']}{i:02}.{data['tenant'].custom_fields.dns_zone.name}",
                cluster=data['cluster'],
                platform=data['platform'],
                tenant=data['tenant'],
                status=VirtualMachineStatusChoices.STATUS_PLANNED,
            )
            vm.save()

            vm.custom_field_data = {
                "vm_prefix": data["prefix"].pk
            }
            vm.save()
            self.log_success(f"Created new VM: {vm}")

        # Generate a CSV table of new VMs
        output = [
            'name,platform'
        ]
        for vm in VirtualMachine.objects.filter(status=VirtualMachineStatusChoices.STATUS_PLANNED):
            attrs = [
                vm.name,
                vm.platform.name,
            ]
            output.append(','.join(attrs))

        return '\n'.join(output)
