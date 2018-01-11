import boto3
import datetime

cloudwatchBilling = boto3.client('cloudwatch', region_name='us-east-1') # Billing is only exposed on us-east-1, cause reasons >.>

def get_billing():

    # Fetch all 'Estimated Charge' metrics
    billing_metrics = cloudwatchBilling.list_metrics(MetricName=u'EstimatedCharges', Namespace=u'AWS/Billing')
    stats = get_metric_details(billing_metrics[u'Metrics'])

    # SSML markup for output
    speech_total = 'Your current total is: <say-as interpret-as="unit">USD' + str(stats[u'Currency']) + '</say-as>. '
    del stats[u'Currency']

    speech_service = 'Here is your itemised bill: '
    for key, value in stats.items():
        speech_service += key + ', <say-as interpret-as="unit">USD' + str(value) + '</say-as>. '

    speech_output = '<speak>Here you go! ' + speech_total + speech_service + '</speak>'

    # Setup the response
    return speech_output

def get_metric_details(metrics):

    stats = {}
    end = datetime.datetime.now()
    start = end - datetime.timedelta(hours=18)
    # print ('Retrieving statistics from %s to %s.\n' % (start, end))
    for metric in metrics:

        metricname = metric[u'Dimensions'][0].get(u'Name')

        # Gather values for metrics
        metricdata = cloudwatchBilling.get_metric_statistics(Namespace=metric[u'Namespace'], MetricName=metric[u'MetricName'], Dimensions=metric[u'Dimensions'], StartTime=start, EndTime=end, Statistics=['Maximum'], Period=3600)
        if metricdata[u'Datapoints']:

            datapoints = metricdata[u'Datapoints']
            datapoints = sorted(datapoints, key=lambda datapoint: datapoint[u'Timestamp'], reverse=True)
            value = datapoints[0][u'Maximum']
            
            # Only show services with cost
            if value > 0:
                if metricname == "ServiceName":
                    metricname = metric[u'Dimensions'][0].get(u'Value')

                if u'LinkedAccount' not in metric[u'Dimensions']:            
                    key = "%s" % (metricname)
                    stats[key] = value
                else:
                    key = "LinkedAccounts.%s.%s" % (metricdata[u'Dimensions'][u'LinkedAccount'][0], metricname)
                    stats[key] = value

                # print ("%s : %f" % (key, value))
    return stats