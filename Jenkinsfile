pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    stages {

        stage('dev') {
            agent {
                docker {
                    image 'governmentpaas/cf-cli'
                    args '-u root'
                }
            }

            environment {
                CLOUDFOUNDRY_API = credentials('CLOUDFOUNDRY_API')
                CF_DOMAIN = credentials('CF_DOMAIN')
                DEV_SECURITY = credentials('DEV_SECURITY')
                CF_USER = credentials('CF_USER')

                NOTIFY_EMAIL_VERIFICATION_TEMPLATE = credentials('NOTIFY_EMAIL_VERIFICATION_TEMPLATE')
                NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = credentials('NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE')
                NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = credentials('NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE')
                NOTIFY_ACCOUNT_LOCKED_TEMPLATE = credentials('NOTIFY_ACCOUNT_LOCKED_TEMPLATE')
            }
            steps {
                sh "cf login -a https://${env.CLOUDFOUNDRY_API} --skip-ssl-validation -u ${CF_USER_USR} -p ${CF_USER_PSW} -o rmras -s dev"
                sh 'cf push --no-start ras-party-dev'
                sh 'cf set-env ras-party-dev ONS_ENV dev'
                sh 'cf set-env ras-party-dev RABBITMQ_AMQP CHANGEME'
                sh "cf set-env ras-party-dev SECURITY_USER_NAME ${env.DEV_SECURITY_USR}"
                sh "cf set-env ras-party-dev SECURITY_USER_PASSWORD ${env.DEV_SECURITY_PSW}"

                sh "cf set-env ras-party-dev CASE_SERVICE_HOST casesvc-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev CASE_SERVICE_PORT 80"

                sh "cf set-env ras-party-dev COLLECTION_EXERCISE_SERVICE_HOST collectionexercisesvc-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev COLLECTION_EXERCISE_SERVICE_PORT 80"

                sh "cf set-env ras-party-dev SURVEY_SERVICE_HOST surveysvc-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev SURVEY_SERVICE_PORT 80"

                sh "cf set-env ras-party-dev NOTIFY_EMAIL_VERIFICATION_TEMPLATE ${env.NOTIFY_EMAIL_VERIFICATION_TEMPLATE}"
                sh "cf set-env ras-party-dev NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE ${env.NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE}"
                sh "cf set-env ras-party-dev NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE ${env.NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE}"
                sh "cf set-env ras-party-dev NOTIFY_ACCOUNT_LOCKED_TEMPLATE ${env.NOTIFY_ACCOUNT_LOCKED_TEMPLATE}"

                sh "cf set-env ras-party-dev IAC_SERVICE_HOST iacsvc-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev IAC_SERVICE_PORT 80"

                sh "cf set-env ras-party-dev OAUTH_SERVICE_HOST ras-django-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev OAUTH_SERVICE_PORT 80"

                sh 'cf start ras-party-dev'
            }
        }

        stage('ci?') {
            agent none
            steps {
                script {
                    try {
                        timeout(time: 60, unit: 'SECONDS') {
                            script {
                                env.deploy_ci = input message: 'Deploy to CI?', id: 'deploy_ci', parameters: [choice(name: 'Deploy to CI', choices: 'no\nyes', description: 'Choose "yes" if you want to deploy to CI')]
                            }
                        }
                    } catch (ignored) {
                        echo 'Skipping ci deployment'
                    }
                }
            }
        }

        stage('ci') {
            agent {
                docker {
                    image 'governmentpaas/cf-cli'
                    args '-u root'
                }

            }
            when {
                environment name: 'deploy_ci', value: 'yes'
            }

            environment {
                CLOUDFOUNDRY_API = credentials('CLOUDFOUNDRY_API')
                CF_DOMAIN = credentials('CF_DOMAIN')
                CI_SECURITY = credentials('CI_SECURITY')
                CF_USER = credentials('CF_USER')

                NOTIFY_EMAIL_VERIFICATION_TEMPLATE = credentials('NOTIFY_EMAIL_VERIFICATION_TEMPLATE')
                NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = credentials('NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE')
                NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = credentials('NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE')
                NOTIFY_ACCOUNT_LOCKED_TEMPLATE = credentials('NOTIFY_ACCOUNT_LOCKED_TEMPLATE')
            }
            steps {
                sh "cf login -a https://${env.CLOUDFOUNDRY_API} --skip-ssl-validation -u ${CF_USER_USR} -p ${CF_USER_PSW} -o rmras -s ci"
                sh 'cf push --no-start ras-party-ci'
                sh 'cf set-env ras-party-ci ONS_ENV ci'
                sh 'cf set-env ras-party-ci RABBITMQ_AMQP CHANGEME'
                sh "cf set-env ras-party-ci SECURITY_USER_NAME ${env.CI_SECURITY_USR}"
                sh "cf set-env ras-party-ci SECURITY_USER_PASSWORD ${env.CI_SECURITY_PSW}"

                sh "cf set-env ras-party-ci CASE_SERVICE_HOST casesvc-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci CASE_SERVICE_PORT 80"

                sh "cf set-env ras-party-ci COLLECTION_EXERCISE_SERVICE_HOST collectionexercisesvc-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci COLLECTION_EXERCISE_SERVICE_PORT 80"

                sh "cf set-env ras-party-ci SURVEY_SERVICE_HOST surveysvc-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci SURVEY_SERVICE_PORT 80"

                sh "cf set-env ras-party-ci NOTIFY_EMAIL_VERIFICATION_TEMPLATE ${env.NOTIFY_EMAIL_VERIFICATION_TEMPLATE}"
                sh "cf set-env ras-party-ci NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE ${env.NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE}"
                sh "cf set-env ras-party-ci NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE ${env.NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE}"
                sh "cf set-env ras-party-ci NOTIFY_ACCOUNT_LOCKED_TEMPLATE ${env.NOTIFY_ACCOUNT_LOCKED_TEMPLATE}"


                sh "cf set-env ras-party-ci IAC_SERVICE_HOST iacsvc-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci IAC_SERVICE_PORT 80"

                sh "cf set-env ras-party-ci OAUTH_SERVICE_HOST ras-django-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci OAUTH_SERVICE_PORT 80"
                sh 'cf start ras-party-ci'
            }
        }

        stage('release?') {
            agent none
            steps {
                script {
                    try {
                        timeout(time: 60, unit: 'SECONDS') {
                            script {
                                env.do_release = input message: 'Do a release?', id: 'do_release', parameters: [choice(name: 'Deploy to test', choices: 'no\nyes', description: 'Choose "yes" if you want to create a tag')]
                            }
                        }
                    } catch (ignored) {
                        echo 'Skipping test deployment'
                    }
                }
            }
        }

        stage('release') {
            agent {
                docker {
                    image 'node'
                    args '-u root'
                }

            }
            environment {
                GITHUB_API_KEY = credentials('GITHUB_API_KEY')
            }
            when {
                environment name: 'do_release', value: 'yes'
            }
            steps {
                // Prune any local tags created by any other builds
                sh "git tag -l | xargs git tag -d && git fetch -t"
                sh "git remote set-url origin https://ons-sdc:${GITHUB_API_KEY}@github.com/ONSdigital/ras-party.git"
                sh "npm install -g bmpr"
                sh "bmpr patch|xargs git push origin"
            }
        }

        stage('test') {
            agent {
                docker {
                    image 'governmentpaas/cf-cli'
                    args '-u root'
                }

            }
            when {
                environment name: 'do_release', value: 'yes'
            }

            environment {
                CLOUDFOUNDRY_API = credentials('CLOUDFOUNDRY_API')
                CF_DOMAIN = credentials('CF_DOMAIN')
                TEST_SECURITY = credentials('TEST_SECURITY')
                CF_USER = credentials('CF_USER')

                NOTIFY_EMAIL_VERIFICATION_TEMPLATE = credentials('NOTIFY_EMAIL_VERIFICATION_TEMPLATE')
                NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = credentials('NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE')
                NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = credentials('NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE')
                NOTIFY_ACCOUNT_LOCKED_TEMPLATE = credentials('NOTIFY_ACCOUNT_LOCKED_TEMPLATE')
            }
            steps {
                sh "cf login -a https://${env.CLOUDFOUNDRY_API} --skip-ssl-validation -u ${CF_USER_USR} -p ${CF_USER_PSW} -o rmras -s test"
                sh 'cf push --no-start ras-party-test'
                sh 'cf set-env ras-party-test ONS_ENV test'
                sh 'cf set-env ras-party-test RABBITMQ_AMQP CHANGEME'
                sh "cf set-env ras-party-test SECURITY_USER_NAME ${env.TEST_SECURITY_USR}"
                sh "cf set-env ras-party-test SECURITY_USER_PASSWORD ${env.TEST_SECURITY_PSW}"

                sh "cf set-env ras-party-test CASE_SERVICE_HOST casesvc-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test CASE_SERVICE_PORT 80"

                sh "cf set-env ras-party-test COLLECTION_EXERCISE_SERVICE_HOST collectionexercisesvc-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test COLLECTION_EXERCISE_SERVICE_PORT 80"

                sh "cf set-env ras-party-test SURVEY_SERVICE_HOST surveysvc-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test SURVEY_SERVICE_PORT 80"

                sh "cf set-env ras-party-test NOTIFY_EMAIL_VERIFICATION_TEMPLATE ${env.NOTIFY_EMAIL_VERIFICATION_TEMPLATE}"
                sh "cf set-env ras-party-test NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE ${env.NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE}"
                sh "cf set-env ras-party-test NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE ${env.NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE}"
                sh "cf set-env ras-party-test NOTIFY_ACCOUNT_LOCKED_TEMPLATE ${env.NOTIFY_ACCOUNT_LOCKED_TEMPLATE}"

                sh "cf set-env ras-party-test IAC_SERVICE_HOST iacsvc-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test IAC_SERVICE_PORT 80"

                sh "cf set-env ras-party-test OAUTH_SERVICE_HOST ras-django-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test OAUTH_SERVICE_PORT 80"
                sh 'cf start ras-party-test'
            }
        }
    }

    post {
        always {
            cleanWs()
            dir('${env.WORKSPACE}@tmp') {
                deleteDir()
            }
            dir('${env.WORKSPACE}@script') {
                deleteDir()
            }
            dir('${env.WORKSPACE}@script@tmp') {
                deleteDir()
            }
        }
    }
}