import oci
import logging

def do_image_query(client, compid):
    pagelist = []

    imageresponse = client.list_images(compartment_id=compid)
    imagelist = imageresponse.data

    while True:
        try:
            nextpage = imageresponse.headers["opc-next-page"]
        except KeyError:
            break

        pagelist.append(nextpage)
        imageresponse = client.list_images(compartment_id=compid, page = nextpage)
        imagelist += imageresponse.data

    return imagelist

def do_subnet_query(client, compid):
    pagelist = []

    vcnresponse = client.list_vcns(compartment_id=compid)
    vcnlist = vcnresponse.data

    while True:
        try:
            nextpage = vcnresponse.headers["opc-next-page"]
        except KeyError:
            break

        pagelist.append(nextpage)
        vcnresponse = client.list_vcns(compartment_id=compid, page = nextpage)
        vcnlist += vcnresponse.data

    for vcn in vcnlist:
        subnetresponse = client.list_subnets(vcn_id = vcn.id, compartment_id=compid)
        subnetlist = subnetresponse.data
        
        while True:
            try:
                nextpage = subnetresponse.headers["opc-next-page"]
            except KeyError:
                break

            pagelist.append(nextpage)
            subnetresponse = client.list_subnets(vcn_id = vcn.id, compartment_id=compid, page = nextpage)
            subnetlist += subnetresponse.data

    return subnetlist

def do_instance_query(client, compid):
    pagelist = []

    instanceresponse = client.list_instances(compartment_id=compid)
    instancelist = instanceresponse.data

    while True:
        try:
            nextpage = instanceresponse.headers["opc-next-page"]
        except KeyError:
            break

        pagelist.append(nextpage)
        instanceresponse = client.list_instances(compartment_id=compid, page = nextpage)
        instancelist += instanceresponse.data

    return instancelist

def do_AD_query(client, compid):
    pagelist = []

    ADresponse = client.list_availability_domains(compartment_id=compid)
    ADlist = ADresponse.data

    while True:
        try:
            nextpage = ADresponse.headers["opc-next-page"]
        except KeyError:
            break

        pagelist.append(nextpage)
        ADresponse = client.list_availability_domains(compartment_id=compid, page = nextpage)
        ADlist += ADresponse.data

    return ADlist

# This one needs the root compartment (tenancy) OCID
def do_compartment_query(client, compid):
    def compartment_crawl(client, crawllist, outputlist):
        pagelist = []
        complist = []

        for compid in crawllist:
            response = client.list_compartments(compartment_id=compid)
            complist += response.data

            while True:
                try:
                    nextpage = response.headers["opc-next-page"]
                except KeyError:
                    break

                pagelist.append(nextpage)
                response = client.list_compartments(compartment_id=compid, page = nextpage)
                complist += response.data

        crawllist = []
        for item in complist:
            outputlist.append({"name":item.description, "ocid":item.id})
            if client.list_compartments(compartment_id=item.id) != "":
                crawllist.append(item.id)
    
        if crawllist == []:
            return outputlist
        else:
            return compartment_crawl(client, crawllist, outputlist)
            
    crawllist = [compid]
    outputlist = [{"name":"Root tenancy", "ocid":compid}]
    return compartment_crawl(client, crawllist, outputlist)

# This returns the private and public IPs associated with an instance
def do_IP_query(computeclient, netclient, compid, instanceid):
    public_ip_list = []
    private_ip_list = []

    vnicresponse = computeclient.list_vnic_attachments(compartment_id = compid, instance_id = instanceid)
    vniclist = vnicresponse.data

    for vnic in vniclist:
        vnicresponse = netclient.get_vnic(vnic_id = vnic.vnic_id)
        private_ip_list.append(vnicresponse.data.private_ip)
        public_ip_list.append(vnicresponse.data.public_ip)
    
    return private_ip_list, public_ip_list

def loadOracleConfig(clouddict):
    oracleConfig = {}
    oracleConfig["user"] = clouddict["user_ocid"]
    oracleConfig["key_content"] = clouddict["api_private_key"]
    oracleConfig["fingerprint"] = clouddict["user_fingerprint"]
    oracleConfig["tenancy"] = clouddict["tenancy_ocid"]
    oracleConfig["region"] = clouddict["region"]
    return oracleConfig

# This function will translate the flavours returned by the VM poller to the names used by the flavour poller
def translateFlavor(shape, shape_config):
    flavor = "o" + str(int(shape_config.ocpus))

    if "E5" in shape:
        flavor += "amd"
    elif "Standard3" in shape:
        flavor += "intel"
    elif "A1" in shape:
        flavor += "arm"

    return flavor

def translateStatus(status):
    if status == "STARTING" or status == "PROVISIONING":
        return "BUILD"
    elif status == "RUNNING":
        return "ACTIVE"
    elif status == "ERROR":
        return status
    else:
        return "ERROR"
