const video = document.getElementById('video')
const imgcanvas = document.getElementById('show-img')
const videocontainer = document.querySelector('.video-container')
const attendButton = document.querySelector('#attend-button')
const studentName = document.getElementById("student-name")
const studentID = document.getElementById("student-id")
const errorContainer = document.getElementById("error-message")
const showModalButton = document.getElementById('show-modal');
const closeModalButton = document.getElementById('close-modal');
const modal = document.getElementById('modal');
const body = document.body;
const mainContent = document.getElementById("main-content")
const modaltext = document.querySelector(".response-modal-text")

const displaySize = { width: video.width, height: video.height }

attendButton.addEventListener('click', (e) => {
  e.preventDefault()
  takephoto();
})


Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri("/static/models"),
  faceapi.nets.faceLandmark68Net.loadFromUri("/static/models"),
  faceapi.nets.faceRecognitionNet.loadFromUri("/static/models"),
  faceapi.nets.faceExpressionNet.loadFromUri("/static/models")
]).then(startVideo)

function startVideo() {
  navigator.mediaDevices.getUserMedia(
    { audio: false, video: {} },
  ).then(stream => {
    video.srcObject = stream
  }).catch(err => {
    console.error(err)
  })
}


function takephoto() {
  const ctx = imgcanvas.getContext('2d');
  imgcanvas.width = displaySize.width;
  imgcanvas.height = displaySize.height;

  /*
  -------------NOTE TO MYSELF-----------:
  1. u have to draw the img on a hidden canvas 
  2. then u can use buit in methods to convert canvas to img/blob etc...
  3. formdata expects and blob
  4. toBlob is an async function, thus unless
      the fetch request is in the callback, it will be 
      executed first thus uploading empty image to backend
  */

  ctx.drawImage(video, 0, 0, displaySize.width, displaySize.height);

  const formData = new FormData();

  imgcanvas.toBlob((blob) => {
    if (blob instanceof Blob) {
      console.log("Blob created");
      formData.append('image', blob, 'photo.jpeg');
      formData.append("student-id", studentID.value);
      formData.append("student-name", studentName.value);

      const csrfToken = getCookie('csrftoken');
      showModal("Loading", 0)
      fetch(`${window.location.origin}/match/registerface/`, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrfToken,
        },
      })
        .then(response => {

          if (response.status === 400) {
            showModal("Error : Student already exists", 400)
            throw new Error('Student exists');
          }
          else if (response.status === 500) {
            showModal("Server Error", 500)
            throw new Error('Server error');
          }
          return response.json()
        })
        .then(data => {
          if(data.photo_path.includes("backblazeb2.com")){
            showModal("Student Registered Successfully", 200)
          }
          
        })
        .catch(error => {
          console.log('Error uploading image:', error);
        });
    } else {
      console.log("Blob not created.");
    }
  }, "image/jpeg", 0.95);
}


/*
  django will automatically generate a csrf token and send to client
  it expects the token to be explictly defined in each request
*/

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}



video.addEventListener('playing', () => {
  const canvas = faceapi.createCanvasFromMedia(video)
  // create canvas with same width and height as video
  console.log(canvas)
  //document.body.append(canvas)
  videocontainer.append(canvas)
  faceapi.matchDimensions(canvas, displaySize)
  setInterval(async () => {
    // detect all faces
    const detections = await faceapi.detectAllFaces(
      video,
      new faceapi.TinyFaceDetectorOptions()
    ).withFaceLandmarks();
    // the lines may be off, correct them
    const resizedDetections = faceapi.resizeResults(detections, displaySize)
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
    faceapi.draw.drawDetections(canvas, resizedDetections)
    faceapi.draw.drawFaceLandmarks(canvas, resizedDetections)
  }, 50)
})


const showModal = (content, status) => {
  modal.style.display = 'block';
  if (status === 400 || status === 500) {
    modal.className = "error-response-modal";
    modaltext.innerText = "";
    modaltext.innerText = content;
    closeModalButton.style.display = "inline-block";
  }
  else if (status === 200) {
    modal.className = "success-response-modal";  
    modaltext.innerText = "";
    modaltext.innerText = content;
    closeModalButton.style.display = "inline-block";
  }
  else if (status === 0) {
    modaltext.innerText = "";
    modal.className = "loader";  
    closeModalButton.style.display = "none";
  }

  // Add the modal text
  mainContent.style.filter = 'blur(5px)';
};

// Function to hide the modal
const closeModal = () => {
  modal.style.display = 'none';
  mainContent.style.filter = 'none';
};
closeModalButton.addEventListener('click', closeModal);

