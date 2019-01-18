dev_appserver.py app.yaml 
## curl -H "Content-Type: application/json" --data @photoPortrait.json "http://localhost:8080/info" 
## curl -H "Content-Type: application/json" --data @photoPortrait.json "http://localhost:8080/info" 
"gsutil cp -r gs://cmosquera-dev.appspot.com/* ." 
gcloud app deploy -v imageapi-py27 
gcloud app deploy -v imageapi-py27-v2 
"pip install GoogleAppEngineCloudStorageClient -t lib" 
curl -H "Content-Type: application/json" --data @photoPortrait.json "https://cmosquera-dev.appspot.com/info" 
