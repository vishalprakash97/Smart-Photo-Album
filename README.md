# Smart Photo Album
*AI photo album with voice-based and text-based search using NLP*
### Description
* A user can add photos through the web app hosted on S3
* LF1 (Lambda) uses Rekognition to generate labels for images and uploads them onto an ES index
* Any user can search the album using text or voice
* LF2 uses Lex to extract keywords and queries the ES index to generate results
* Use CodePipeline to implement CI/CD for Lambda function and frontend
* CloudFormation template represents all infrastructure resources

### Architecture
<img src="Images/architecture.png" width=400>

### Tech Stack
AWS (S3, API Gateway, Lambda, ElasticSearch, CodePipeline, Cloud Formation, Transcribe, Lex, Rekognition), Python, Javascript

### Contributors

* Vishal Prakash (vp2181@nyu.edu)
* Vedang Mondreti (vm2129@nyu.edu)
