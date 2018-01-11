import boto3
from grammar import it_plurality, is_plurality, server_plurality
from pprint import pprint

ec2_resource = boto3.resource('ec2')

ec2_client = boto3.client('ec2')
ec2_autoscaling = boto3.client('autoscaling')


def get_service_status(slots):

    if slots["Label"]["value"] is None:
        raise ValueError("No 'Label' slot was set")
    else:
        environment = slots["Label"]["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]

    instances = get_instance_by_filter(name="tag:Environment", values=environment[u'name'])

    if len(instances[u'Online']) == len(instances[u'Tagged']):
        speech_output = "I found " + str(len(instances[u'Tagged'])) + " " + server_plurality(instances[u'Tagged']) + " labelled as " +  environment[u'name'] + ", all of wich are online."
    else:
        speech_output = "I found " + str(len(instances[u'Tagged'])) + " " + server_plurality(instances[u'Tagged']) + " labelled as " +  environment[u'name'] +  ", however " + str(len(instances[u'Offline'])) + " " + server_plurality(instances[u'Offline']) + " " + is_plurality(instances[u'Offline']) + " offline."

    speech_output = '<speak>'+speech_output+'</speak>'

    return speech_output

def set_service_status(slots):

    if slots["Label"]["value"] is None:
        raise ValueError("No 'Label' slot was set")
    else:
        environment = slots["Label"]["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]

    if slots["State"]["value"] is None:
        raise ValueError("No 'State' slot was set")
    else:
        state = slots["State"]["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]

    instances = get_instance_by_filter(name="tag:Environment", values=environment[u'name'])

    if state["id"] == "START":
        if instances[u'Offline']:
            ec2_client.start_instances(InstanceIds=instances[u'Offline'])
            speech_output = "I found " + str(len(instances[u'Offline'])) + " " + server_plurality(instances[u'Offline']) + " labelled as " +  environment[u'name'] + ", I have now started " + it_plurality(instances[u'Offline'])
        else:
            speech_output = "I didn't find any offline servers labelled as " +  environment[u'name']
    elif state["id"] == "STOP":
        if instances[u'Online']:
            ec2_client.stop_instances(InstanceIds=instances[u'Online'])
            speech_output = "I found " + str(len(instances[u'Online'])) + " " + server_plurality(instances[u'Online']) + " labelled as " +  environment[u'name'] + ", I have now stopped "  + it_plurality(instances[u'Online'])
        else:
            speech_output = "I didn't find any online servers labelled as " +  environment[u'name']

    speech_output = '<speak>'+speech_output+'</speak>'

    return speech_output

def set_autoscaling_instances(slots):

    if slots["Type"]["value"] is None:
        raise ValueError("No 'Type' slot was set")
    else:
        service_type = slots["Type"]["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"][u'name']

    if slots["InstanceNumber"]["value"] is None:
        raise ValueError("No 'InstanceNumber' slot was set")
    else:
        instance_number = slots["InstanceNumber"]["value"]

    response = ec2_autoscaling.set_desired_capacity(
        AutoScalingGroupName="Backend",
        DesiredCapacity=int(instance_number)
    )

    speech_output = "I have scaled the group: " +  service_type + " to " + instance_number

    speech_output = '<speak>'+speech_output+'</speak>'

    return speech_output

def get_instance_by_filter(name, values):

    filters = [{
        'Name': name,
        'Values': [values]
    }]

    instances = ec2_resource.instances.filter(Filters=filters)
    
    instance_data = {}
    tagged_instances = []
    online_instances = []
    offline_instances = []

    for instance in instances:
        tagged_instances.append(instance.id)
        # http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Instance.state
        if instance.state['Code'] == 16:
            online_instances.append(instance.id)
        else:
            offline_instances.append(instance.id)

    instance_data = {
        'Tagged' : tagged_instances,
        'Online' : online_instances,
        'Offline' : offline_instances
    }

    return instance_data