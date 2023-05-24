import sys
import time
import boto3
import string
import random
from flask import current_app
from ctf.models import Config as dbConfig
from botocore.client import Config
from botocore.exceptions import ClientError
import json

class AWS():

	def __init__(self):
		try:
			# set timeouot to higher
			config_dict = {'region_name': 'eu-west-2', 'connect_timeout': 5, 'read_timeout': 300}
			config = Config(**config_dict)
			# get the boto3 creds
			ACCESS_KEY = dbConfig.query.filter(dbConfig.key=="access_key").first().value
			SECRET_KEY = dbConfig.query.filter(dbConfig.key=="secret_key").first().value
			# get ec2 instance and resource for each region
			self.ec2 = {"eu-west-2":boto3.client('ec2', region_name="eu-west-2", config=config,
				    aws_access_key_id=ACCESS_KEY,
				   	aws_secret_access_key=SECRET_KEY),
				"eu-west-1":boto3.client('ec2', region_name="eu-west-1", config=config,
					aws_access_key_id=ACCESS_KEY,
				   	aws_secret_access_key=SECRET_KEY),
				"eu-west-3":boto3.client('ec2', region_name="eu-west-3", config=config,
					aws_access_key_id=ACCESS_KEY,
				   	aws_secret_access_key=SECRET_KEY),
				"eu-central-1":boto3.client('ec2', region_name="eu-central-1", config=config,
					aws_access_key_id=ACCESS_KEY,
				   	aws_secret_access_key=SECRET_KEY),
			}
			# get ec2 resource for each region
			self.ec2_resource = {"eu-west-2":boto3.resource('ec2', region_name="eu-west-2", config=config,
					aws_access_key_id=ACCESS_KEY,
				   	aws_secret_access_key=SECRET_KEY),
				"eu-west-1":boto3.resource('ec2', region_name="eu-west-1", config=config,
					aws_access_key_id=ACCESS_KEY,
				   	aws_secret_access_key=SECRET_KEY),
				"eu-west-3":boto3.resource('ec2', region_name="eu-west-3", config=config,
					aws_access_key_id=ACCESS_KEY,
				   	aws_secret_access_key=SECRET_KEY),
				"eu-central-1":boto3.resource('ec2', region_name="eu-central-1", config=config,
					aws_access_key_id=ACCESS_KEY,
				   	aws_secret_access_key=SECRET_KEY)
			}
			# get vpc we use for each region
			self.vpc_id={"eu-west-2":self.ec2["eu-west-2"].describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', ''),
				"eu-west-1":self.ec2["eu-west-1"].describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', ''),
				"eu-central-1":self.ec2["eu-central-1"].describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', ''),
				"eu-west-3":self.ec2["eu-west-3"].describe_vpcs().get('Vpcs', [{}])[0].get('VpcId', '')
			}
			# get security group we use for each region
			self.sec_groups={
				"eu-central-1":"sg-0bcaf7a6093d0406e",
				"eu-west-1":"sg-0c049676115d58ae3",
				"eu-west-2":"sg-03e2cf718e180d524"
			}
			# regions we use
			self.regions = ["eu-central-1","eu-west-1","eu-west-2"]

		except Exception as e:
			# it didnt initialize so raise it and forget it
			print(str(e))
			pass

	def __get_instances(self, region, instances=[]):
		try:
			r = self.ec2[region].describe_instances(InstanceIds=instances)
			if len(r["Reservations"][0]["Instances"]) > 0:
				return r["Reservations"][0]["Instances"]
			else:
				raise Exception("Could not find any instances with instance ids (%s)" % instances)
		except:
			raise Exception("Could not find any instances with instance ids (%s)" % instances)

	def create_server(self, challenge_name, team_name, ami, instance_type="t2.small"):
		# MAX_DATA_DISK = 16384
		# get a random region
		ami = json.loads(ami)
		region = random.choice(self.regions)
		# get the security group id for the region
		security_group_id = self.sec_groups[region]
		# get the remote provider id returned from when creating the instance
		server_name = "{} ({})".format(challenge_name, team_name)
		remote_provider_id = self.__create_instance(server_name, security_group_id, instance_type, ami=ami[region], region=region)
		# we need to sleep to get ip because its not assigned immediately
		time.sleep(5)
		public_ip_v4 = self.__get_instances(region,[remote_provider_id])[0]["PublicIpAddress"]
		# wait until its running
		while True:
			status = self.__get_instances(region,[remote_provider_id])[0]["State"]["Name"]
			if (status != "running"):
				time.sleep(10)
			else:
				time.sleep(10)
				break
		return public_ip_v4, remote_provider_id, region

	def set_instance_unused(self, region, remote_provider_id):
		# set tag unused to false
		self.ec2[region].create_tags(Resources=[remote_provider_id], Tags=[{"Key":"in_use","Value":"False"}])

	def get_unused_instance(self, instance_type="t2.small"):
		filters = [
			{'Name': 'tag:in_use', 'Values': ['False']},
			{'Name': 'instance-state-name', 'Values' : ['running']},
			{'Name': 'instance-type', 'Values' : [instance_type]}
                ]
		# for each region try and find an unused server
		for region in self.regions:
			reservations = self.ec2[region].describe_instances(
				Filters=filters).get('Reservations',[])
			# if there is an instance available
			if len(reservations) > 0:
				instances = reservations[0].get("Instances",[])
				if len(instances) > 0:
					instance = instances[0]
					# set it to inuse
					self.ec2[region].create_tags(Resources=[instance['InstanceId']], Tags=[{"Key":"in_use","Value":"True"}])
					return instance['PublicIpAddress'], instance["InstanceId"], region
		# if there is no server in any region
		raise Exception("No challenge servers left!")

	def __create_instance(self, server_name, security_group, instance_type, ami, region):
		try:
			tags = [{"ResourceType":"instance","Tags":[{"Key":"Name","Value":server_name}]}]
			# create the instance without a data disk
			instances = self.ec2_resource[region].create_instances(ImageId=ami, MinCount=1, MaxCount=1, TagSpecifications=tags, InstanceType=instance_type, KeyName="main", NetworkInterfaces=[{"Groups":[security_group],"DeviceIndex":0,"AssociatePublicIpAddress": True}])
			return instances[0].instance_id
		except Exception as e: raise

	def delete_server(self, remote_id, region):
		try:
			self.__delete_instance(remote_id, region)
		except Exception as e: raise

	def __delete_instance(self, instance_id, region):
		try:
			result = self.ec2[region].terminate_instances(InstanceIds=[instance_id])
			if len(result["TerminatingInstances"]) == 0:
				raise Exception("AWS Instance ("+instance_id+") could not be terminated. (Unknown Reason)")
		except ClientError as e:
			error_code = sys.exc_info()[1].response["Error"]["Code"]
			if error_code != 'InvalidInstanceID.NotFound':
				raise 
		except Exception as e: raise

