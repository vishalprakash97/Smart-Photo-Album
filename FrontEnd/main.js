// Calls the API /search?q="""
function submitSearch(e) {

    var apigClient = apigClientFactory.newClient();

    var params = {
        'q': document.getElementById("input-search").value,
    };

    apigClient.searchGet(params, {}, {})
        .then(function(result) {
            displayImage(result);
        }).catch(function(result) {
            console.log(result);
        });
}

// voice search
function submitVoice(file) {

    var file_name = "Recording.wav";

    var apigClient = apigClientFactory.newClient();

    var additionalParams = {
        headers: {
            'Content-Type': file.type,
        }
    }

    url = "https://7awy9zawok.execute-api.us-east-1.amazonaws.com/v1/upload/photoalbum-audiosearch-a2/" + file_name
    axios.put(url, file, additionalParams).then(response => {

        var params = {
            'q': 'searchAudio',
        };

        apigClient.searchGet(params, {}, {}).then(function(result) {
            displayImage(result);
        }).catch(function(result) {
            console.log('wait... still searching')
        });
        console.log("Voice uploaded: " + file_name);
    });

}

function displayImage(result) {
    console.log("result", result);

    img_paths = JSON.parse(result["data"]["body"])
    var div = document.getElementById("imgDiv");
    div.innerHTML = '<h2>Photo Grid</h2>';

    var j;
    console.log(typeof(img_paths))
    console.log("Entering for loop")
    for (j = 0; j < img_paths.length; j++) {
        console.log(img_paths[j])
        img_ls = img_paths[j].split('/');
        img_name = img_ls[img_ls.length - 1];
        div.innerHTML += '<div class="col-md-3 mx-auto"><div class="card text-dark"><img src="' + img_paths[j] + '" class="card-img-top"><div class="card-body">' +
            '<p class="card-text">' + img_name + '</p></div ></div ></div >';
    }
}


function submitPhoto(e) {

    if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
        alert('The File APIs are not fully supported in this browser.');
        return;
    }

    var path = (document.getElementById("input-file").value).split("\\");
    customLabels = document.getElementById("input-customLabels").value;
    var file_name = path[path.length - 1];

    console.log(file_name);
    console.log("pritning custom labels")
    console.log(customLabels);

    var file = document.getElementById("input-file").files[0];
    console.log(file);

    if (customLabels.length != 0) {
        var headers = {
            'Content-Type': file.type,
            'x-amz-meta-customlabels': customLabels
        };
    } else {
        var headers = {
            'Content-Type': file.type,
        };
    }

    console.log(headers)

    console.log(file.name.split('.')[0])

    url = "https://7awy9zawok.execute-api.us-east-1.amazonaws.com/v1/upload/photoalbum-a2/" + file.name
    axios.put(url, file, { headers: headers }).then(response => {
        console.log(response)
        alert("Image uploaded: " + file.name);
    }).catch(function(result) {
        console.log("result", result);
    });

}