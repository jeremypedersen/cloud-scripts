#
# Author: Jeremy Pedersen
# Updated: 2023-10-27
# 
# This helper script helps generate aws-nuke CLI invocations and config.yaml files
# to clean up test environments. As written, the `config.yaml` file assumes:
# 1. We do not want to clean the Organization management (root) account
# 2. We do not want to remove the OrganizationAccountAccessRole or its permissions
# 3. We do not want to try to delete un-deletable resources (OSPackage)
#
# The script takes as input a CSV file in which the first two columns are:
# 1. AWS Account ID of management (root) account
# 2. AWS account ID of organization (member) account
#
# The generated `aws-nuke` commands are written to a new output file
# This file and the generated .yaml files are stored in in a directory 
# called `nuke` which the script will attempt to create, because the organization
# may contain quite a few accounts, an we want to keep things clean
#
import argparse
import csv
import os
import boto3

#############
# Functions # 
#############

def get_root_account_id():
    # Create an STS client
    sts_client = boto3.client('sts')
    
    # Get the caller identity
    response = sts_client.get_caller_identity()
    
    # Extract and return the account ID
    account_id = response['Account']
    
    return account_id

def generate_nuke_commands(input, output):
    # Config string to follow
    config_string = "aws-nuke -c config-{}.yaml --assume-role-arn arn:aws:iam::{}:role/OrganizationAccountAccessRole --no-dry-run"

    # Config file pattern to follow
    # (note config must not be indented to avoid accidentally adding 
    # extra tabs into the string literal)
    config_pattern = '''
---
regions:
  - global
  - us-east-1

account-blocklist:
  - {}

accounts:
    {}:
      presets:
        - "common"

resource-types:
# Don't nuke OSPackage stuff, it isn't deletable anyway
  excludes:
    - OSPackage

# Don't remove AWS Organizations permissions sets
presets:
  common:
    filters:
      IAMRole:
        - "OrganizationAccountAccessRole"
      IAMRolePolicyAttachment:
        - "OrganizationAccountAccessRole -> AdministratorAccess"
'''.strip()

    # Check if the directory exists
    if os.path.exists(output):
        print(f"Warning: The directory '{output}' already exists, exiting.")
        exit(-1)
    else:
        # Create the directory if it doesn't exist
        os.mkdir(output)
        print(f"Directory '{output}' created successfully.")

    # Open input file for reading
    fin = open(input, 'r')
    reader = csv.reader(fin)
    next(reader, None) # Skip header row

    # Open output file for writing
    fout = open(f'{output}/commands.csv', 'w')
    writer = csv.writer(fout)
    writer.writerow(['Account', 'Command'])

    # Look up account ID for Org owner
    org_id = get_root_account_id()

    for row in reader:
        member_id = row[0]

        # Write config file to disk
        config = open(f'{output}/config-{member_id}.yaml', 'w')
        config.write(config_pattern.format(org_id, member_id))
        config.close()

        # Write config string to output file
        writer.writerow([member_id, config_string.format(member_id, member_id)])

    # Close out files
    fin.close()
    fout.close()

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description="Script to generate 'aws-nuke' command invocations and associated config files, for cleaning AWS accounts")
parser.add_argument('-i', '--input', type=str, required=True, help="Input CSV file, containing account IDs: first column is the Organizations owner account, second column is the member account ID.")
parser.add_argument('-o', '--output', type=str, required=True, help="Output directory in which to store 'aws-nuke' commands and config files.")
args = parser.parse_args()

generate_nuke_commands(args.input, args.output)
print('Done!')
