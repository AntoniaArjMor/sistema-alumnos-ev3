// Jenkinsfile - Pipeline de "Sistema Alumnos" (SecureDev · Evaluación Parcial 3 · OCY1102)
//
// Esta es la versión BASE: construye, prueba y despliega en producción.
// Los marcadores  >>> [ETIQUETA]  indican dónde agregar las etapas de seguridad.
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 40, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    // Revisa GitHub cada ~3 minutos: cada push (tuyo o un PR de Dependabot fusionado) dispara un build.
    triggers {
        pollSCM('H/3 * * * *')
    }

    environment {
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        APP_SECRET_KEY = credentials('app-secret-key')
        ADMIN_CLAVE_HASH = credentials('admin-clave-hash')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    // Versión = 1.0.<nº de build>+<commit corto>: une cada despliegue con su commit (trazabilidad)
                    def sha = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    env.APP_VERSION = "1.0.${env.BUILD_NUMBER}+${sha}"
                }
                echo "Versión de este build: ${env.APP_VERSION}"
                sh 'git log -1 --format="Commit %h de %an: %s"'
                // Cada build parte limpio: sin reportes viejos y con un entorno virtual nuevo
                sh 'rm -rf .venv reports && mkdir -p reports'
                sh 'python3 -m venv .venv'
                sh '.venv/bin/pip install --quiet -r requirements.txt -r requirements-dev.txt'
                sh '.venv/bin/python -m compileall -q app.py'
            }
        }

        stage('Test') {
            steps {
                sh '.venv/bin/python -m pytest --junitxml=reports/junit.xml'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('Security Review (SAST)') {
    steps {
        script {
            sh 'bandit -q app.py -f json -o reports/bandit.json --exit-zero'

            def resultado = sh(
                script: 'bandit -ll app.py -o reports/bandit.txt',
                returnStatus: true
            )

            sh 'cat reports/bandit.txt'

            if (resultado != 0) {
                unstable('Bandit detecto hallazgos o errores')
            }
        }
    }
}

        stage('Dependency Management') {
            steps {
                script {
                    def resultado = sh(
                        script: 'pip-audit -r requirements.txt -r requirements-dev.txt -o reports/pip-audit.txt',
                        returnStatus: true
                    )

                    def resultadoJson = sh(
                        script: 'pip-audit -r requirements.txt -r requirements-dev.txt -f json -o reports/pip-audit.json',
                        returnStatus: true
                    )

                    sh 'cat reports/pip-audit.txt'

                    if (resultado != 0 || resultadoJson != 0) {
                        unstable('Dependencias vulnerables o error de auditoria')
                    }
                }
            }
        }

            stage('Deploy Staging') {
        steps {
            sh 'bash scripts/deploy.sh staging 5001'
        }
    }

        stage('DAST - OWASP ZAP') {
            steps {
                script {
                    def resultado = sh(
                        script: 'python3 scripts/zap_scan.py http://jenkins:5001',
                        returnStatus: true
                    )

                    if (resultado == 2) {
                        unstable('ZAP encontro alertas High o Medium')
                    } else if (resultado != 0) {
                        error('Error durante la ejecucion de OWASP ZAP')
                    }
                }
            }
        }

        stage('Deploy Producción') {
                        when {
                expression {
                    currentBuild.currentResult == 'SUCCESS'
                }
            }
            steps {
                sh 'bash scripts/deploy.sh produccion 5000'
                script { env.PRODUCCION = env.APP_VERSION }
            }
        }
    }

    post {
        always {
            // Registro de trazabilidad: build <-> versión <-> commit <-> pruebas <-> hallazgos <-> despliegue
            withEnv(["RESULTADO=${currentBuild.currentResult}"]) {
                sh 'python3 scripts/trazabilidad.py'
            }
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}
