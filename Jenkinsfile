#!/usr/bin/env groovy
node {
  stage('git checkout') {
    step([$class: 'WsCleanup'])
    final scmVars = checkout(
      [$class: 'GitSCM',
       branches: [[name: '*/master']],
       doGenerateSubmoduleConfigurations: false,
       extensions: [
        [$class: 'CloneOption', depth: 0, noTags: false, reference: '', shallow: false]],
       userRemoteConfigs: [
         [credentialsId: 'hmrc-githubcom-service-infra-user-and-pat',
          url: 'https://github.com/HMRC/txm-s3-log-shipper-lambda.git']]]
    )
    sh("echo ${scmVars.GIT_BRANCH} | cut -f 2 -d '/' > .git/_branch")
  }
  stage('Prepare python environment') {
    sh('make ci_docker_build')
  }
  stage('setup') {
    sh('make ci_setup')
  }
  stage('test') {
    sh('make ci_test')
  }
  stage('security') {
    sh('make ci_security_checks')
  }
  stage('package') {
    sh('make ci_package')
  }
  stage('publish') {
    sh('make ci_publish')
  }
}
