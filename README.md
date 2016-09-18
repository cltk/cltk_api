[![Build Status](https://travis-ci.org/cltk/cltk_api.svg?branch=master)](https://travis-ci.org/cltk/cltk_api) [![Join the chat at https://gitter.im/cltk/cltk_api](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/cltk/cltk_api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

# About

This is a RESTful web API for the CLTK.


# Use and deployment with Docker
Following basic Kubernetes directions for integrating with Google Cloud Compute: <http://kubernetes.io/docs/hellonode/>.

``` bash
export PROJECT_ID="cltk-api"
```

``` bash
docker build -t cltk_api .
docker run -d -p 5000:5000 --name cltk_api cltk_api
curl http://localhost:5000/
```

Setup for running on Google Cloud:

``` bash
docker build -t gcr.io/$PROJECT_ID/cltk-api:v1 .
docker run -d -p 5000:5000 --name cltk_api gcr.io/$PROJECT_ID/cltk-api:v1
```

Test with:

``` bash
curl http://localhost:5000
```

Push container to Google's container registry:
``` bash
gcloud docker push gcr.io/$PROJECT_ID/cltk-api:v1
```

Now create a cluster:

``` bash
gcloud config set compute/zone us-west1-a
gcloud container clusters create --machine-type f1-micro --num-nodes 3 cltk-api-cluster
gcloud container clusters get-credentials cltk-api-cluster
```

Create a pod (a group of containers):

``` bash
kubectl run cltk-api --image=gcr.io/$PROJECT_ID/cltk-api:v1 --port=5000
```

Get the outside-facing IP of this pod:

``` bash
kubectl get deployments
```

Allow outside traffic:

``` bash
kubectl expose deployment cltk-api --type="LoadBalancer"
```

Get external IP (see `EXTERNAL_IP`):

``` bash
$ kubectl get services cltk-api
NAME       CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
cltk-api   10.3.250.7   104.198.9.132   5000/TCP   1m
```

Now test the API:

``` bash
curl 104.198.9.132:5000/hello
```

To push a code update:

``` bash    
docker build -t gcr.io/$PROJECT_ID/cltk-api:v2 .
gcloud docker push gcr.io/$PROJECT_ID/cltk-api:v2
```

``` bash
kubectl set image deployment/cltk-api cltk-api=gcr.io/$PROJECT_ID/cltk-api:v2
```


## License

The CLTK is Copyright (c) 2016 Kyle P. Johnson, under the MIT License. See [LICENSE](https://github.com/cltk/cltk/blob/master/LICENSE) for details.