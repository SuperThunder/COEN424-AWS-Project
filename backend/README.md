# Requirements
- AWS CLI environment with credentials installed
- AWS CDK installed


# Setup (from nothing)
1. Setup a python virtualenv and install the requirements
1. Run `cdk synth` and `cdk deploy` in the backend directory
1. Wait for the OpenSearch domain to come online (can take 20-30 minutes)
1. Create the wifinetworks index in OpenSearch with the geo_point mapping (see 'Creating geo_point index')
    - required and must be done before ANY POSTs to the submit API
    - the master credentials for OpenSearch basic auth can be found in AWS secrets manager

# Updating stack (after initial creation)
1. Source your python venv
1. Run `cdk synth` and `cdk deploy` in the backend directory

# Creating geo_point index
PUT to <opensearch_domain>/wifinetworks with authorization and json body of:
```
{
    "mappings": {
            "properties": {
                "location": { 
                    "type": "geo_point" 
                } 
            } 
    } 
}
```


# Welcome to your CDK Python project!

You should explore the contents of this project. It demonstrates a CDK app with an instance of a stack (`backend_stack`)
which contains an Amazon SQS queue that is subscribed to an Amazon SNS topic.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization process also creates
a virtualenv within this project, stored under the .venv directory.  To create the virtualenv
it assumes that there is a `python3` executable in your path with access to the `venv` package.
If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv
manually once the init process completes.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

You can now begin exploring the source code, contained in the hello directory.
There is also a very trivial test included that can be run like this:

```
$ pytest
```

To add additional dependencies, for example other CDK libraries, just add to
your requirements.txt file and rerun the `pip install -r requirements.txt`
command.

## Tutorial  
See [this useful workshop](https://cdkworkshop.com/30-python.html) on working with the AWS CDK for Python projects.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
