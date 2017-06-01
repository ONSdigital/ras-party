set -o pipefail
py.test swagger_server/test_local --cov=swagger_server/controllers_local --cov-report xml
