# DeepRacer Scripts

Scripts to help setup and manage [AWS DeepRacer](https://docs.aws.amazon.com/deepracer/latest/developerguide/what-is-deepracer.html).

## `dr-create-users.py`

This script creates a set of DeepRacer users. It takes a number as input.

If the user inputs `10`, the script will create new IAM users called `deepracer_1` through `deepracer_10`. If the user inputs `100`, the users will be `deepracer_1` through `deepracer_100`. 

The script also creates an IAM user group called `DeepRacerUsers` and attaches two IAM policies:

```
arn:aws:iam::aws:policy/AWSDeepRacerDefaultMultiUserAccess
arn:aws:iam::aws:policy/IAMUserChangePassword
```

The script takes each new IAM user and adds them to the `DeepRacerUsers` group, then **writes a `users.csv` file to disk**.

The file contains (on each line) a username, password, and IAM logon URL.

The script can be safely re-run: it will simply skip any steps that cannot be successfully completed (using Python's `try/except`).

## `dr-delete-users.py`

This script deletes all the resources created by `dr-create-users.py`. 

Note that the script will fail to remove the user group if any additional IAM policies have been added to the group beyond the ones added by `dr-create-users.py`.

**Warning:** This script deletes any IAM user prefixed with `deepracer`. **Not just users created by `dr-create-users.py`.**

This script can also be safely re-run.