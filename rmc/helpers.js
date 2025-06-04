import Swal from "sweetalert2";
import "bootstrap/dist/css/bootstrap.min.css";

export function displayError(errorMessage,title) {

  console.log(errorMessage);
  let htmlContent = `<b><i>${errorMessage.message} (Code: ${errorMessage.code})</i></b>`;

  if (errorMessage.detail && errorMessage.detail.length > 0) {
    htmlContent += '<ul>';
    errorMessage.detail.forEach(detailItem => {
      // htmlContent += `<li>${detailItem}</li>`;
      htmlContent += '<li>';
      Object.entries(detailItem).forEach(([key, value]) => {
        htmlContent += `<strong>${key}:</strong> ${value}<br>`;
      });
      htmlContent += '</li>';
    });
    htmlContent += '</ul>';
  }
  Swal.fire({
    title: '<img src="/error-icon.png" width="110" height="60"/>' + title,
    html: htmlContent,
    customClass: {
      popup: 'swal-wide',
      icon: 'error'
    },
    })
}

export function displayErrorToast(titleMessage) {
  
  var snackbar = document.getElementById("snackbar");
  var icon =document.getElementById("snackbar-icon");
  if (icon) {
    icon.src= "/error-icon.png";
    icon.height = '40';
    icon.width = '90';
  }
  
  var title = document.getElementById("snackbar-title");
  title.innerText = titleMessage;
  snackbar.className = "show error";
  setTimeout(function(){ snackbar.className = snackbar.className.replace("show", ""); }, 3000);
}

export function displaySuccessToast(titleToast) {
  
    var snackbar = document.getElementById("snackbar");
    var icon =document.getElementById("snackbar-icon");
    icon.src= "./img/success-icon.png";
    icon.height = '50';
    icon.width = '40';
   // snackbar.style.height = '300px';
    var title = document.getElementById("snackbar-title");
    title.innerText = titleToast;
    snackbar.className = "show success";
    setTimeout(function(){ snackbar.className = snackbar.className.replace("show", ""); }, 3000);
      }
    
export function parseBoolean(booleanString) {

  return (booleanString && String(booleanString).toLowerCase() === 'true');
}    
export function parseBooleanToString(booleanValue){
  return (booleanValue?'Yes':'No');
}
