#!/usr/bin/env groovy
pipeline {
  agent {
        label 'commonslave'
  }
  stages {
      stage('git checkout') {
        steps {
            step([$class: 'WsCleanup'])
            checkout(scm)
        }
      }
      stage('Prepare python environment') {
        steps {
            sh('make ci_docker_build')
        }
      }
      stage('setup') {
        steps {
            sh('make ci_setup')
        }
      }
      stage('test') {
        steps {
            sh('make ci_test')
        }
      }
      stage('security') {
        steps {
            sh('make ci_security_checks')
        }
      }
      stage('package') {
        steps {
            sh('make ci_package')
        }
      }
      stage('publish') {
        steps {
            sh('make ci_publish')
        }
      }
  }
}
