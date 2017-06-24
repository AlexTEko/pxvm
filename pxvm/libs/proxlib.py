import random
from proxmoxer import ProxmoxAPI


class Prox:

    def __init__(self, proxmox_host, password, user: str = 'root@pam', verify_ssl=True, port=443):
        self.prox = ProxmoxAPI(proxmox_host, user=user, password=password, port=port, verify_ssl=verify_ssl)

    def get_version(self):
        return self.prox.version.get()

    def get_nodes(self):
        return self.prox.nodes.get()

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

    def __generate_ip(self, ip_mask):
        all_ips = [ip_mask.format(x) for x in range(201, 251)]
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

    def create_lxc(self, ostemplate, ip, gw, ssh, hostname=None, node='pve',
                   storage='tank', memory=512, swap=512, cores=1, rootfs='8', online=True, bridge='vmbr0'):
        new_vmid = self.__get_vm_id()
        if ip == 'dhcp':
            net0 = 'name=eth0,bridge={},ip=dhcp'.format(bridge)
        else:
            ip = self.__generate_ip(ip)
            net0 = 'name=eth0,bridge={},ip={},gw={}'.format(bridge, ip, gw)
        self.prox.nodes(node).lxc.create(**{'vmid': new_vmid, 'ostemplate': ostemplate, 'hostname': hostname,
                                            'storage': storage, 'memory': memory, 'swap': swap, 'cores': cores,
                                            'rootfs': rootfs, 'ssh-public-keys': ssh, 'net0': net0})
        if online:
            self.control_vm(new_vmid, 'start')

        return {'config': self.prox.nodes(node).lxc(new_vmid).config.get(), 'ip': ip.split('/')[0]}

    def get_tasks(self, vmid=None):
        tasks = self.prox.cluster.tasks.get()
        if vmid:
            return [x for x in sorted(tasks, key=lambda k: str(k['starttime']), reverse=True) if x['id'] == str(vmid)]
        return sorted(tasks, key=lambda k: str(k['starttime']), reverse=True)
