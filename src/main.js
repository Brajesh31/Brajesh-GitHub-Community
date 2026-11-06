function run() {
    var followerList = document.getElementById("list");

    readTextFile("Dataset.json", function (text) {
        var data;
        try {
            data = JSON.parse(text);
        } catch (error) {
            followerList.textContent = "The follower report is unavailable.";
            return;
        }

        data.forEach(function (profile) {
            var link = document.createElement("a");
            link.href = "https://github.com/" + encodeURIComponent(profile[0]);
            var image = document.createElement("img");
            image.src = profile[1];
            image.alt = profile[0];
            image.width = 50;
            image.height = 50;
            link.appendChild(image);
            followerList.appendChild(link);
        });
    }, function () {
        followerList.textContent = "The follower report is unavailable.";
    });
}

function readTextFile(file, callback, errorCallback) {
    var rawFile = new XMLHttpRequest();
    rawFile.overrideMimeType("application/json");
    rawFile.open("GET", file, true);
    rawFile.onreadystatechange = function () {
        if (rawFile.readyState !== 4) {
            return;
        }
        if (rawFile.status === 200) {
            callback(rawFile.responseText);
        } else if (errorCallback) {
            errorCallback();
        }
    };
    rawFile.send(null);
}
