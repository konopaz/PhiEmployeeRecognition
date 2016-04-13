# PhiEmployeeRecognition - Project for CS419

## Development Process

### Pre-reqs
Python 2.7, PIP, and virtualenv installed. Python 2.7 is a requirement because it's the supported
version used by AWS Elastic Bean Stalk. PIP and virtualenv are used to define the execution
environment in a portable way.

### Initial Setup
First checkout the repo someplace convenient..

    cd ~/projects/ #or someplace else convenient
    git clone https://github.com/konopaz/PhiEmployeeRecognition.git

You should have a new PhiEmployeeRecognition directory. Now use virtualenv and pip to spin up the
environment.

    virtualenv PhiEmployeeRecognition
    cd PhiEmployeeRecognition
    source bin/activate
    pip install -r requirements.txt

NOTE - you must run the source bin/activate or the pip install command will install the package
globally - not to the local virtualenv.

After running source bin/activate your shell prompt will change to indicate that you're running
inside the virtualenv.

At this point you should be able to run the application with...

    python application.py

The output of that command should tell you to access the application at http://127.0.0.1:5000/

## Useful sites for reference
* [Bootstrap](http://getbootstrap.com/)
* [AWS Setup 1](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-common-steps.html)
* [AWS Setup 2](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html)


**Testing access 