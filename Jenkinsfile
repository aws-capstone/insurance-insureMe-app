pipeline{
    
    agent any
    
    tools{
        maven 'mymaven'
    }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION    = 'us-east-1'
        ANSIBLE_HOST_KEY_CHECKING = 'False'
        DOCKER_USERNAME = credentials('docker-username')  // Jenkins stored credential for Docker username
        DOCKER_PASSWORD = credentials('docker')  // Jenkins stored credential for Docker password        

    }    
    
    parameters {
        booleanParam(name: 'autoApprove', defaultValue: false, description: 'Automatically run apply after generating plan?')
        choice(name: 'action', choices: ['apply', 'destroy'], description: 'Select the action to perform')
        booleanParam(name: 'autoApproveProd', defaultValue: false, description: 'Automatically run apply after generating plan for PROD?')
        choice(name: 'actionProd', choices: ['apply', 'destroy'], description: 'Select the action to perform')        
    }
    
    stages{
        stage('Clone Repository')
        {
            steps{
                git credentialsId: 'github_token-nikitaks97', url: 'https://github.com/aws-capstone/insurance-insureMe-app.git'
            }
        }
        stage('Test Code')
        {
            steps{
                sh 'mvn test'
            }
        }
        stage('Build Code')
        {
            steps{
                sh 'mvn package'
            }
        }
        stage('Build Image')
        {
            steps{
                sh 'docker build -t capstone_project1:$BUILD_NUMBER .'
            }
        }

        stage('Push the Image to dockerhub')
        {
            steps{
                
        withCredentials([string(credentialsId: 'docker', variable: 'docker')]) 
                {
               sh 'docker login -u  nikitaks997797 -p ${docker} '
               }
                sh 'docker tag capstone_project1:$BUILD_NUMBER nikitaks997797/capstone_project1:$BUILD_NUMBER'
                sh 'docker push nikitaks997797/capstone_project1:$BUILD_NUMBER'
            }
        }
        stage('Terraform Init'){
            steps{
                dir('terraform'){
                  sh ' ls -lrt'
                  sh 'terraform  init'
                }
            }
        }
        stage('Terraform Plan'){
            steps{
                dir('terraform'){
                  sh 'terraform plan -out tfplan'
                  sh 'terraform show -no-color tfplan > tfplan.txt'
                }
            }
        }
        stage('Apply / Destroy') {
            steps {
                dir('terraform'){
                script {
                    if (params.action == 'apply') {
                        if (!params.autoApprove) {
                            def plan = readFile 'tfplan.txt'
                            input message: "Do you want to apply the plan?",
                            parameters: [text(name: 'Plan', description: 'Please review the plan', defaultValue: plan)]
                        }
                        sh 'terraform ${action} -input=false tfplan'
                    } else if (params.action == 'destroy') {
                        sh 'terraform ${action} --auto-approve'
                    } else {
                        error "Invalid action selected. Please choose either 'apply' or 'destroy'."
                    }
                }
                script {
                    def output = sh(script: 'terraform output -json instance_public_ip', returnStdout: true).trim()
                    env.EC2_PUBLIC_IP = output.replaceAll('"', '') // Remove quotes if JSON returns them
                }
                }
            }
        }
        stage('Generate Ansible Hosts File') {
            steps {
                script {
                    // Write the public IP to the Ansible hosts file
                    writeFile file: 'hosts', text: """
                    [webserver]
                    ${env.EC2_PUBLIC_IP} ansible_user=ubuntu ansible_ssh_private_key_file=./terraform/insureme-test-ec2.pem
                    """
                }
            }
        }
        stage('Configure Test Server with Ansible') {
            steps {
                // Run the Ansible playbook using the generated hosts file
                sh 'sleep 60'
                sh 'ansible-playbook -i hosts ansible/playbook_docker.yml'
                sh 'ansible-playbook -i hosts ansible/playbook_selenium.yml'
            }
        }
        stage('Deploy to Test Server') {
            steps {
                // Run the Ansible playbook using the generated hosts file
                //sh 'echo "Disabled for test"'
                //sh 'ansible-playbook -i hosts ansible/playbook_deploy.yml --extra-vars "BUILD_NUMBER=${BUILD_NUMBER}"'
                sh 'ansible-playbook -i hosts ansible/playbook_deploy.yml --extra-vars "BUILD_NUMBER=13"'
            }
        }
        stage('Test the application') {
            steps {
                // Run the Ansible playbook using the generated hosts file
                sh 'ansible-playbook -i hosts ansible/playbook_test_app.yml'
            }
        }
        stage('Terraform Init Prod'){
            steps{
                dir('terraform-prod'){
                  //sh ' ls -lrt'
                  sh 'terraform  init'
                }
            }
        }
        stage('Terraform Plan Prod'){
            steps{
                dir('terraform-prod'){
                  sh 'terraform plan -out tfplan'
                  sh 'terraform show -no-color tfplan > tfplan.txt'
                }
            }
        }
        stage('Apply / Destroy Prod') {
            steps {
                dir('terraform-prod'){
                script {
                    if (params.actionProd == 'apply') {
                        if (!params.autoApproveProd) {
                            def plan = readFile 'tfplan.txt'
                            input message: "Do you want to apply the plan?",
                            parameters: [text(name: 'Plan', description: 'Please review the plan', defaultValue: plan)]
                        }
                        sh 'terraform ${actionProd} -input=false tfplan'
                    } else if (params.actionProd == 'destroy') {
                        sh 'terraform ${actionProd} --auto-approve'
                    } else {
                        error "Invalid action selected. Please choose either 'apply' or 'destroy'."
                    }
                }
                script {
                    def output = sh(script: 'terraform output -json instance_public_ip', returnStdout: true).trim()
                    env.EC2_PUBLIC_IP = output.replaceAll('"', '') // Remove quotes if JSON returns them
                }
                }
            }
        }
        stage('Generate Ansible Prod Hosts File') {
            steps {
                script {
                    // Write the public IP to the Ansible hosts file
                    writeFile file: 'hosts-prod', text: """
                    [webserver]
                    ${env.EC2_PUBLIC_IP} ansible_user=ubuntu ansible_ssh_private_key_file=./terraform-prod/insureme-prod-ec2.pem
                    """
                }
            }
        }
        stage('Configure Prod Server with Ansible') {
            steps {
                // Run the Ansible playbook using the generated hosts file
                sh 'sleep 60'
                sh 'ansible-playbook -i hosts-prod ansible/playbook_docker.yml'
            }
        }
        stage('Deploy to Prod Server') {
            steps {
                // Run the Ansible playbook using the generated hosts file
                //sh 'echo "Disabled for test"'
                sh 'ansible-playbook -i hosts-prod ansible/playbook_deploy.yml --extra-vars "BUILD_NUMBER=${BUILD_NUMBER}"'
            }
        }                                                 
    }
}
