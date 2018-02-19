import boto3
import inflect

ec2_resource = boto3.resource('ec2')

ec2_client = boto3.client('ec2')
ec2_autoscaling = boto3.client('autoscaling')

p = inflect.engine()

# GetServicesIntent
def get_service_status(slots):

    environment = get_slot(slots,"Label")

    instances = get_instance_by_filter(name="tag:Environment", values=environment[u'name'])

    speech_output = "I found " + str(len(instances[u'Tagged'])) + p.plural(" server", len(instances[u'Tagged'])) + " labelled as " +  environment[u'name'] + ". "

    if len(instances[u'Online']) == len(instances[u'Tagged']):
        speech_output += "All of wich are online."
    else:
        speech_output += "However " + str(len(instances[u'Offline'])) + " " + p.plural("server", len(instances[u'Offline'])) + p.plural(" is", len(instances[u'Offline'])) + " offline."

    speech_output = '<speak>'+speech_output+'</speak>'

    return speech_output

# ManageServicesIntent
def set_service_status(slots):

    environment = get_slot(slots,"Label")
    state = get_slot(slots, "State")

    instances = get_instance_by_filter(name="tag:Environment", values=environment[u'name'])

    if state["id"] == "START":
        if instances[u'Offline']:
            ec2_client.start_instances(InstanceIds=instances[u'Offline'])
            speech_output = "I found " + str(len(instances[u'Offline'])) + " " + p.plural("server",len(instances[u'Offline'])) + " labelled as " +  environment[u'name'] + ", I have now started " + p.plural("it",len(instances[u'Offline']))
        else:
            speech_output = "I didn't find any offline servers labelled as " +  environment[u'name']
    elif state["id"] == "STOP":
        if instances[u'Online']:
            ec2_client.stop_instances(InstanceIds=instances[u'Online'])
            speech_output = "I found " + str(len(instances[u'Online'])) + " " +  p.plural("server",len(instances[u'Online'])) + " labelled as " +  environment[u'name'] + ", I have now stopped "  + p.plural("server",len(instances[u'Online']))
        else:
            speech_output = "I didn't find any online servers labelled as " +  environment[u'name']

    speech_output = '<speak>'+speech_output+'</speak>'

    return speech_output

# ScaleServicesIntent
def set_autoscaling_instances(slots):

    service_type = get_slot(slots,"Type")
    instance_number = get_slot(slots,"InstanceNumber")

    ec2_autoscaling.set_desired_capacity(
        AutoScalingGroupName="Backend",
        DesiredCapacity=int(instance_number)
    )

    speech_output = "I have scaled the group: " +  service_type + " to " + instance_number

    speech_output = '<speak>'+speech_output+'</speak>'

    return speech_output

# Main function for getting instance data
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

# Helper function to resolve slot value
def get_slot(slots, name):
    if slots[name]["value"] is None:
        raise ValueError("No " + name + " slot was set")

    if slots[name]["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"] is None:
        environment = slots[name]["value"]
    else:
        # Synonym resolver
        environment = slots[name]["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]
    
    return environment