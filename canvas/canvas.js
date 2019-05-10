function addImage(i, j, url) {
    fabric.Image.fromURL(url, function(oImg) {
      canvas.add(oImg);
      oImg.top = i;
      oImg.left = j;
    });
}

function addKilledImage(i, j, url) {
    fabric.Image.fromURL(url, function(oImg) {
      canvas.add(oImg);
      oImg.top = i;
      oImg.left = j;
      canvas.forEachObject(function(o) {
        canvas.remove(o);
      });
      canvas.clear();
      canvas.renderAll();
    });
}

function killAll(canvas) {

}

function loadSceneImages(scene, sceneIndex) {
    console.log("images to load: ", scene.length)
    // console.log("scene: ", scene)
    var images = [];
    var loadCount = 0;
    for (j = 0; j < scene.length; j++) {
        console.log("scene: ", j)
        imEntity = scene[j];
        // console.log(imEntity[0]);
        var url = imEntity[0].toString();
        // console.log(url);
        var row = imEntity[1][0][0];
        var col = imEntity[1][0][1];
        var u = imEntity[1][0][2];

        var width = imEntity[2][0];
        var height = imEntity[2][1];

        fabric.Image.fromURL(url, function(oImg) {
          canvas.add(oImg);
          oImg.top = row;
          oImg.left = col;
          images.push(oImg);
          console.log("images : " , images);
          var xScale = width/oImg.width;
          var yScale = height/oImg.height;
          oImg.set({scaleX : xScale, scaleY : yScale});
          loadCount++;
          // console.log("loadCount: ", loadCount);
          if (loadCount == scene.length) {
             // canvas.renderAll();
             function animate(scene) {
                var start = null;
                var framesPassed = 0;

                // Set drawing order based on layer
                for (i = 0; i < scene.length; i++) {
                    // console.log(scene[0][1].length);
                    images[i]['layer'] = scene[i][3];
                }
                canvas._objects.sort(function (a, b) {return a['layer'] - b['layer'];});
                console.log(canvas._objects);

                function animateHelper() {
                    for (i = 0; i < scene.length; i++) {

                        // console.log(scene[0][1].length);
                        imEntity = scene[i];
                        var row = imEntity[1][framesPassed][1] - imEntity[2][0]/2;
                        var col = imEntity[1][framesPassed][0] - imEntity[2][1]/2;
                        var u = imEntity[1][framesPassed][2];
                        images[i].set({'top': row, 'left' : col, 'opacity' : u}).setCoords();
                    }
                    canvas.renderAll();
                    if (framesPassed < scene[0][1].length - 2) {
                        framesPassed++;
                        window.requestAnimationFrame(animateHelper);
                    } else {
                        $(document).trigger("sceneShow" + (sceneIndex + 1).toString());
                        canvas.clear();
                        images = [];
                        console.log("Animate Done");
                    }
                }
                window.requestAnimationFrame(animateHelper);
            }
            animate(scene);
          }
        });

    }
}

function loadCallback(scene, sceneIndex) {
    return function() {
        console.log("scene: ", scene)
        loadSceneImages(scene, sceneIndex);
    }
}

var sceneShowCallbackNumber = 0;

function showAllScenes() {
    // Create an animation string.
    start = sceneShowCallbackNumber;
    for (i = 0; i < titlesAndMotion.length; i++) {
        console.log(titlesAndMotion[i]);
        $(document).bind("sceneShow" + sceneShowCallbackNumber.toString(), loadCallback(titlesAndMotion[i], sceneShowCallbackNumber));
        sceneShowCallbackNumber++;
    }
    $(document).trigger('sceneShow' + start.toString());
}


    // for (i = 0; i < titlesAndMotion.length; i++) {
    //     $(document).bind("sceneShow" + i.toString(), function() {
    //         loadSceneImages(canvas, titlesAndMotion[i], i);
    //     });
    // }
    // $(document).trigger('sceneShow0');