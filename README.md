Hello user!

This is CI/CD DQE testing project. 

Project description.
This project includes: 
- docker file and docker-compose file, which are made to run Jenkins in docker.
- Jenkins pipeline file which should be used for execution of the pipeline. 
This pipeline do following:
    - pull data from DEV branch from the repository (https://github.com/SiarheiZhamoidzik/cicd-first-try)
    - execute pytest autotests from folder /autotests 
    - if autotests passed then DEV branch is merged to RELEASE branch and to MAIN branch. 
    This approach is defined by chosen branching strategy - "Git Flow". So it is supposed that developer make branches for features based on DEV branch. When the feature is merged to DEV brach and this branch is pushed to the remote repository then pipeline should be triggered, run tests and in case of success merge result to other branches.
Pipeline is triggered automatically. It checks every 1 minute the state of the DEV branch and in case if there were changes executes pipeline.

Project structure:
- Folder /autotests - contains pytests for execution. These tests are from previous module "Test Automation For DQE". Tests are executed on AdventureWorks2019 database, which should be stored on the host machine. By default tests should be passed.
- docker-compose.yaml file - contains settings for execution of Dockerfile
- Dockerfile - contains settings for docker image creation
- pipeline.jenkins - Jenkins pipeline settings



