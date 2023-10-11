# EC2 Scripts

Scripts to manage EC2 instances, snapshots, and launch templates. At present, the following scripts are provided: 

- `ec2-list-amis.py`: List all AMIs in a specified region
- `ec2-list-snapshots.py`: List all snapshots in a specified region
- `ec2-snapshot-all.py`: Snapshot all the volumes attached to stopped EC2 instances in a specified region
- `ec2-start.py`: Start all EC2 instances in a specified region 
- `ec2-stop.py`: Stop all EC2 instances in a specified region
- `ec2-terminate-stopped.py`: Terminate all stopped instances in a specified region
- `ec2-update-launch-templates.py`: Set the default version of all launch templates to the latest version of the template, and delete previous versions
- 