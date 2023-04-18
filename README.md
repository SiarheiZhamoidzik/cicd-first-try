Hello user!

This is CI/CD for DQE training project. 

Project description.
This project includes: 
- docker file and docker-compose file, which are made to run Jenkins in docker.
- Jenkins pipeline file which should be used for execution of the pipeline. 
This pipeline do following:
    - pull data from the remote repository (https://github.com/SiarheiZhamoidzik/cicd-first-try)
    - install python libraries from requirements.txt if needed
    - execute pytest autotests from folder /autotests 
    - if autotests passed then DEV branch is merged to RELEASE branch and to MAIN branch. 
    This approach is defined by chosen branching strategy - "Git Flow". So it is supposed that developer make branches for features based on DEV branch. When the feature is merged to DEV brach and this branch is pushed to the remote repository then pipeline should be triggered, run tests and in case of success merge result to other branches.
Pipeline is triggered automatically. It checks every 1 minute the state of the DEV branch and in case if there were changes executes pipeline.

Project structure:
- Folder /autotests - contains pytests for execution. These tests are from previous module "Test Automation For DQE". Tests are executed on AdventureWorks2019 database, which should be stored on the host machine. By default tests should be passed.
- docker-compose.yaml file - contains settings for execution of Dockerfile
- Dockerfile - contains settings for docker image creation
- pipeline.jenkins - Jenkins pipeline settings

How to use:
- Clone repository to local folder
- copy files docker-compose.yaml and Dockerfile to some other folder where docker volume will be stored 
- open command line in this folder 
- run command "docker-compose up" to execute docker-compose file and create docker container
- open http://localhost:8080/ to setup Jenkins
- create Jenkins Pipeline:
    - "Build Triggers" should be set: choose Poll SCM and set schedule like '* * * * *'
    - "Definition" = 'Pipeline script from SCM', Repository URL = 'https://github.com/SiarheiZhamoidzik/cicd-first-try'
    - on GitHub create personal access token (classic) in accordance with https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token (it will be used for mergeing branches and pushing it into remote repository)
    - add personal access token to Jenkins in Manage Jenkins > Manage Credentials > System > Global credentials > Add credentials
    - use this credential in the field "Credentials" in Jenkins pipeline settings and put the name of the credention into the pipeline.jenkins file like "withCredentials([gitUsernamePassword(credentialsId: 'github_test_token', gitToolName: 'Default')])"
    - set "Branch Specifier (blank for 'any')" = '*/dev'
    - set "Script Path" = pipeline.jenkins
- Configuration connection to the Database from the container in accordance with instruction from HW
- Set user and password in file cnx_settings.py
- Run Jenkins pipeline. 
    Expected result: 
        - tests are passed
        - DEV branch is merged to RELEASE and MAIN branches

If pipeline trigger was set properly then it is expected that when user add any changes to dev branch (with PR from any feature branch, for example), then in 1 minute pipeline should be executed automatically.
For that we can do the following:
    - create new local branch based on DEV branch
    - open file Metadata.xlsx in folder /autotest/metadata/
    - for example change name of any column. It should be done to make test fail
    - add, commit changes and push branch to remote repo
    - create PR to DEV branch 
    Expected result:
        - pipeline should be automatically triggered in 1 min
        - test should be failed
        - code should not be merged to DEV and RELEASE branches




