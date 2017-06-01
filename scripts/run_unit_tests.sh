set -o pipefail
py.test --cov=swagger_server/controllers_local --cov-report xml
