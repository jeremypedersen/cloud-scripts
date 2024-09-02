# EC2 scripts

Scripts to manage EC2 instances, snapshots, and launch templates. At present, the following scripts are provided: 

- `ec2-list-amis.py`: List all AMIs in a given region
- `ec2-list-instances.py`: List all EC2 instances in a given region
- `ec2-list-snapshots.py`: List all snapshots in a given region
- `ec2-snapshot-all.py`: Snapshot all volumes in a given region
- `ec2-start.py`: Start all EC2 instances in a given region
- `ec2-stop.py`: Stop all EC2 instances in a given region
- `ec2-terminate-stopped.py`: Terminate all stopped EC2 instances in a given region
- `ec2-update-launch-templates.py`: Update all launch templates in a given region, so that the latest version is the default, and delete older versions
