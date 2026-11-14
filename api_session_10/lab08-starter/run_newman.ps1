# Run Lab 3 Newman API test suite
# Prerequisites:
#   1. npm install -g newman
#   2. Start Flask API in another terminal: python -m app --port 5000

newman run books-api.postman_collection.json `
  -e postman/local.postman_environment.json `
  -r "cli,junit" `
  --reporter-junit-export reports/junit.xml
