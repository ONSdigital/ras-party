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

                RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE = credentials('RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE')
                RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = credentials('RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE')
                RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = credentials('RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE')
            }
            steps {
                sh "cf login -a https://${env.CLOUDFOUNDRY_API} --skip-ssl-validation -u ${CF_USER_USR} -p ${CF_USER_PSW} -o rmras -s dev"
                sh 'cf push --no-start ras-party-dev'
                sh 'cf set-env ras-party-dev ONS_ENV dev'
                sh 'cf set-env ras-party-dev RABBITMQ_AMQP CHANGEME'
                sh "cf set-env ras-party-dev SECURITY_USER_NAME ${env.DEV_SECURITY_USR}"
                sh "cf set-env ras-party-dev SECURITY_USER_PASSWORD ${env.DEV_SECURITY_PSW}"

                sh "cf set-env ras-party-dev RAS_CASE_SERVICE_HOST casesvc-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev RAS_CASE_SERVICE_PORT 80"

                sh "cf set-env ras-party-dev RAS_COLLEX_SERVICE_HOST collectionexercisesvc-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev RAS_COLLEX_SERVICE_PORT 80"

                sh "cf set-env ras-party-dev RAS_SURVEY_SERVICE_HOST surveysvc-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev RAS_SURVEY_SERVICE_PORT 80"

                sh "cf set-env ras-party-dev RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE ${env.RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE}"
                sh "cf set-env ras-party-dev RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE ${env.RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE}"
                sh "cf set-env ras-party-dev RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE ${env.RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE}"

                sh "cf set-env ras-party-dev RAS_IAC_SERVICE_HOST iacsvc-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev RAS_IAC_SERVICE_PORT 80"

                sh "cf set-env ras-party-dev RAS_OAUTH_SERVICE_HOST ras-django-dev.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-dev RAS_OAUTH_SERVICE_PORT 80"

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

                RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE = credentials('RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE')
                RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = credentials('RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE')
                RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = credentials('RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE')
            }
            steps {
                sh "cf login -a https://${env.CLOUDFOUNDRY_API} --skip-ssl-validation -u ${CF_USER_USR} -p ${CF_USER_PSW} -o rmras -s ci"
                sh 'cf push --no-start ras-party-ci'
                sh 'cf set-env ras-party-ci ONS_ENV ci'
                sh 'cf set-env ras-party-ci RABBITMQ_AMQP CHANGEME'
                sh "cf set-env ras-party-ci SECURITY_USER_NAME ${env.CI_SECURITY_USR}"
                sh "cf set-env ras-party-ci SECURITY_USER_PASSWORD ${env.CI_SECURITY_PSW}"

                sh "cf set-env ras-party-ci RAS_CASE_SERVICE_HOST casesvc-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci RAS_CASE_SERVICE_PORT 80"

                sh "cf set-env ras-party-ci RAS_COLLEX_SERVICE_HOST collectionexercisesvc-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci RAS_COLLEX_SERVICE_PORT 80"

                sh "cf set-env ras-party-ci RAS_SURVEY_SERVICE_HOST surveysvc-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci RAS_SURVEY_SERVICE_PORT 80"

                sh "cf set-env ras-party-ci RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE ${env.RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE}"
                sh "cf set-env ras-party-ci RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE ${env.RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE}"
                sh "cf set-env ras-party-ci RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE ${env.RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE}"

                sh "cf set-env ras-party-ci RAS_IAC_SERVICE_HOST iacsvc-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci RAS_IAC_SERVICE_PORT 80"

                sh "cf set-env ras-party-ci RAS_OAUTH_SERVICE_HOST ras-django-ci.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-ci RAS_OAUTH_SERVICE_PORT 80"
                sh 'cf start ras-party-ci'
            }
        }

        stage('test?') {
            agent none
            steps {
                script {
                    try {
                        timeout(time: 60, unit: 'SECONDS') {
                            script {
                                env.deploy_test = input message: 'Deploy to test?', id: 'deploy_test', parameters: [choice(name: 'Deploy to test', choices: 'no\nyes', description: 'Choose "yes" if you want to deploy to test')]
                            }
                        }
                    } catch (ignored) {
                        echo 'Skipping test deployment'
                    }
                }
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
                environment name: 'deploy_test', value: 'yes'
            }

            environment {
                CLOUDFOUNDRY_API = credentials('CLOUDFOUNDRY_API')
                CF_DOMAIN = credentials('CF_DOMAIN')
                TEST_SECURITY = credentials('TEST_SECURITY')
                CF_USER = credentials('CF_USER')

                RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE = credentials('RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE')
                RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = credentials('RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE')
                RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = credentials('RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE')
            }
            steps {
                sh "cf login -a https://${env.CLOUDFOUNDRY_API} --skip-ssl-validation -u ${CF_USER_USR} -p ${CF_USER_PSW} -o rmras -s ci"
                sh 'cf push --no-start ras-party-test'
                sh 'cf set-env ras-party-test ONS_ENV ci'
                sh 'cf set-env ras-party-test RABBITMQ_AMQP CHANGEME'
                sh "cf set-env ras-party-test SECURITY_USER_NAME ${env.TEST_SECURITY_USR}"
                sh "cf set-env ras-party-test SECURITY_USER_PASSWORD ${env.TEST_SECURITY_PSW}"

                sh "cf set-env ras-party-test RAS_CASE_SERVICE_HOST casesvc-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test RAS_CASE_SERVICE_PORT 80"

                sh "cf set-env ras-party-test RAS_COLLEX_SERVICE_HOST collectionexercisesvc-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test RAS_COLLEX_SERVICE_PORT 80"

                sh "cf set-env ras-party-test RAS_SURVEY_SERVICE_HOST surveysvc-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test RAS_SURVEY_SERVICE_PORT 80"

                sh "cf set-env ras-party-test RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE ${env.RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE}"
                sh "cf set-env ras-party-test RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE ${env.RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE}"
                sh "cf set-env ras-party-test RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE ${env.RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE}"

                sh "cf set-env ras-party-test RAS_IAC_SERVICE_HOST iacsvc-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test RAS_IAC_SERVICE_PORT 80"

                sh "cf set-env ras-party-test RAS_OAUTH_SERVICE_HOST ras-django-test.${env.CF_DOMAIN}"
                sh "cf set-env ras-party-test RAS_OAUTH_SERVICE_PORT 80"
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