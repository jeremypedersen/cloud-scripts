# 
# Date: 2023-08-18
# Author: Jeremy Pedersen
#
# Create multiple DeepRacer IAM users, for use with 
# DeepRacer's multi-user feature, documented here:
# https://docs.aws.amazon.com/deepracer/latest/developerguide/multi-user-mode.html
#
import boto3, time

sts = boto3.client('sts')
iam = boto3.client('iam')

# Constants
user_prefix = 'deepracer'
group_name = 'DeepRacerUsers'

# Open file to store usernames
f = open('users.csv', 'w')
f.write('username, password, login link\n')

# Wait for user input (loop on error)
no_input = True
while no_input:
    try:
        num_users = input('Number of DeepRacer users to create: ')
        num_users = int(num_users)
        print(f'OK! Creating {num_users} users...')
        no_input = False
    except:
        print(f'Sorry, {num_users} is not a valid input. Please try again.')

# Determine the IAM user login link for the account (so we can include it
# in the .csv file)
try:
    # Fetch account ID
    account_id = sts.get_caller_identity().get('Account')
    
    # Construct the URL
    login_url = f'https://{account_id}.signin.aws.amazon.com/console/'
    print(f'IAM users can log in using: {login_url}')
except:
    print(f'Could not determine account ID!')
    print('Continuing anyway, but you a will need to determine the IAM user login URL by yourself')
    login_url = 'UNKNOWN'

# Create IAM User Group "DeepRacerUsers", and attach policies 
# to grant DeepRacer service access and IAM "change password" permissions
policy_arns = [
    'arn:aws:iam::aws:policy/AWSDeepRacerDefaultMultiUserAccess',
    'arn:aws:iam::aws:policy/IAMUserChangePassword'
]

try:
    # Create the group
    response = iam.create_group(GroupName=group_name)
    if response and 'Group' in response:
        print(f'Group {group_name} created successfully.')
except:
    print(f'Unable to create group {group_name}, skipping and hoping it is already there!')

# Wait before attaching policies
print('Waiting a few seconds before adding policies...')
time.sleep(5)   

for policy_arn in policy_arns:
    try:
        # Attach the policy to the group
        iam.attach_group_policy(
            GroupName=group_name,
            PolicyArn=policy_arn
        )
        print(f'Policy {policy_arn} attached to group {group_name} successfully.')
    except:
        print(f'Unable to attach policy {policy_arn} to group {group_name}, continuing on...')

# Create users
for i in range(1, num_users+1):
    username = f'{user_prefix}_{i}'
    password = f'{username}_123$' # Assign a predictable password (user will change on first login)
    print('=' * 30) # Print a separator
    print(f'Creating user {username}')

    # Create user
    try:
        iam.create_user(UserName=username)
    except:
        print(f'Cloud not create user: {username}')
        print('Skipping, moving on to next user')

    # Grant console access
    try:
        iam.create_login_profile(
            UserName=username, Password=password, PasswordResetRequired=True)
    except:
        print(f"Could not create login profile for {username}")
        print(f'Continuing anyway...')

    # Grant DeepRacer permissions (assigned to group)
    try:
        iam.add_user_to_group(
            UserName=username,
            GroupName=group_name
        )
    except:
        print(f'Could not add user {username} to group')
        print(f'Continuing anyway...')

    f.write(f'{username}, {password}, {login_url}\n')

# Close the .csv file
f.close()

print('=' * 30) # Print a separator
print('All done!')