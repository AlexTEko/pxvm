import random
from proxmoxer import ProxmoxAPI

DEFAULT_TEMPLATE = 'local:vztmpl/ubuntu-16.04-standard_16.04-1_amd64.tar.gz'
DEFAULT_GW = '10.160.18.1'
DEFAULT_IP = '10.160.18.{}/24'
DEFAULT_PASSWORD = '12345'
SSH_KEYS = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCtbCa4zzsFlQgPmghFLR0FPEwD0XUKWdsQ9UZCVTLBNMtOxkd77aqeLT/f29ICGMnf' \
           'MDV6SfFaxN/uWJukQ0onPTNHTQwyJsxGZdrKBByhS0jBp4SXfoU6KH1gA/m8CykC0WSBzdJRT/1RemYAuC+AzklLthEO/F8gnC97QAWm' \
           'ix7govUrJWFQZ9k8pgybB3YUFu3SSqt/Q5PGfxFW8jmkpxFWi6DrBa4Yfuu7oP7d0p4+nYHbhTRPO0E1sXzZPBijXaVOzFJybgB/pYhX' \
           '8JcpBrVPd3LffVIPfeFiC8b4dk3cX3ITkuzDQn423BzEOfrnlHj2R+WouvXKaHFM+bld root@delta\n'


class Prox:

    def __init__(self, proxmox_host, password, user: str = 'root@pam', verify_ssl=True, port=443):
        self.prox = ProxmoxAPI(proxmox_host, user=user, password=password, port=port, verify_ssl=verify_ssl)

    def get_vms(self, status=None):
        nodes = self.prox.cluster.config.nodes.get()
        vms = []
        for node in nodes:
            vms += self.prox.nodes(node['name']).lxc.get()
            vms += self.prox.nodes(node['name']).qemu.get()
        if status:
            return [x for x in vms if x['status'] == status]
        else:
            return vms

    def get_vms_configs(self):
        nodes = self.prox.cluster.config.nodes.get()
        vms_configs = []
        for node in nodes:
            for vm in self.prox.nodes(node['name']).lxc.get():
                if vm['type'] == 'lxc':
                    vms_configs.append(self.prox.nodes(node['name']).lxc(vm['vmid']).config.get())
                if vm['type'] == 'qemu':
                    vms_configs.append(self.prox.nodes(node['name']).qemu(vm['vmid']).config.get())
        return vms_configs

    def __get_vm_id(self):
        vms = self.get_vms()
        vmid = 1
        for vm in vms:
            if int(vm['vmid']) > int(vmid):
                vmid = vm['vmid']
        vmid = int(vmid) + 1
        return vmid

    def __generate_ip(self):
        all_ips = [DEFAULT_IP.format(x) for x in range(201, 251)]
        ips = []
        vms = self.get_vms_configs()
        for vm in vms:
            if vm.get('net0'):
                net = vm.get('net0').split(',')
                for item in net:
                    if 'ip=' in item:
                        if not 'dhcp' in item:
                           ips.append(item.split('=')[1])
        for ip in ips:
            if ip in all_ips:
                all_ips.remove(ip)
        index = random.randint(0, len(all_ips))
        return all_ips[index]

    def control_vm(self, vmid, status, node='pve'):
        self.prox.nodes(node).lxc(vmid).status.post(status)

    def create_lxc(self, hostname, node='pve', ostemplate=DEFAULT_TEMPLATE,
                   storage='tank', memory=512, swap=512, cores=1, rootfs='8', password=DEFAULT_PASSWORD, online=True,
                   ip=None, bridge='vmbr0', gw=DEFAULT_GW):
        new_vmid = self.__get_vm_id()
        if ip == 'dhcp':
            net0 = 'name=eth0,bridge={},ip=dhcp'.format(bridge)
        else:
            ip = self.__generate_ip()
            net0 = 'name=eth0,bridge={},ip={},gw={}'.format(bridge, ip, gw)
        self.prox.nodes(node).lxc.create(**{'vmid':new_vmid, 'ostemplate': ostemplate, 'hostname': hostname,
                                            'storage': storage, 'memory': memory, 'swap': swap, 'cores': cores, 'rootfs': rootfs,
                                            'ssh-public-keys': SSH_KEYS, 'net0': net0})
        if online:
            self.control_vm(new_vmid, 'start')

        print({'hostname': hostname, 'ip': ip.split('/')[0]})
